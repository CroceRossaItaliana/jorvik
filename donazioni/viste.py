from datetime import datetime
from itertools import chain

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.utils.text import slugify

from anagrafica.models import Sede, Appartenenza
from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA, COMPLETO, ERRORE_PERMESSI, MODIFICA, LETTURA, ERRORE_ORFANO
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico
from base.files import Excel, FoglioExcel
from base.utils import poco_fa
from donazioni.elenchi import ElencoCampagne, ElencoEtichette, ElencoDonazioni, ElencoDonatori
from donazioni.forms import (ModuloCampagna, ModuloEtichetta, ModuloDonazione, ModuloDonatore,
                             ModuloImportDonazioni, ModuloImportDonazioniMapping, ModuloInviaNotifica, ModuloImportaMailUp)
from donazioni.models import Campagna, Etichetta, Donatore, Donazione, AssociazioneDonatorePersona, SedeCampagnaFittizia
from donazioni.utils import (donazioni_per_mese_anno, donazioni_chart_52_settimane,
                             invia_mail_ringraziamento, invia_notifica_donatore, crea_lista_mailup, iscrivi_email)
from donazioni.utils_importazione import analizza_file_import
from ufficio_soci.models import Quota


@pagina_privata
def donazioni_home(request, me):
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    donatori = Donatore.objects.filter(donazioni__campagna__in=campagne).distinct('id')
    fondi_raccolti = Donazione.objects.filter(campagna__in=campagne).aggregate(totale=Sum('importo'))
    sedi_gestite = Sede.objects.none()
    if me.ha_permesso(GESTIONE_CAMPAGNE):
        # delegato campagne
        sedi_gestite = me.oggetti_permesso(GESTIONE_CAMPAGNE)
    contesto = {
        'sedi_gestite': sedi_gestite,
        'campagne_gestite': campagne,
        'donatori': donatori,
        'fondi_raccolti': fondi_raccolti['totale'] or 0
    }
    return 'donazioni.html', contesto


@pagina_privata
def donazioni(request, me):
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA).values_list('id')
    donazioni = Donazione.objects.filter(campagna__in=campagne).prefetch_related('campagna', 'donatore')
    elenco = ElencoDonazioni(donazioni)
    contesto = {
        'elenco': elenco,
    }
    return 'donazioni_elenco.html', contesto


@pagina_privata
def campagne_elenco(request, me):

    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    elenco = ElencoCampagne(campagne)
    contesto = {
        'campagne': campagne,
        'elenco': elenco,
        'puo_creare': me.ha_permesso(GESTIONE_CAMPAGNE),
    }
    return 'donazioni_campagne_elenco.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def campagna_nuova(request, me):

    modulo = ModuloCampagna(request.POST or None, initial={"inizio": datetime.now()})

    if modulo.is_valid():
        campagna = modulo.save()
        request.session['campagna_creata'] = campagna.pk
        sede = campagna.organizzatore
        if sede.mailup:
            id_lista = crea_lista_mailup(campagna)
            campagna.id_lista_mailup = id_lista
            campagna.save()
        return redirect(campagna.url_responsabili)

    contesto = {
        'modulo': modulo
    }
    return 'donazioni_campagna_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNA,))
def campagna_modifica(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloCampagna(request.POST or None, instance=campagna)

    if modulo.is_valid():
        campagna = modulo.save()
        return redirect(campagna.url)

    contesto = {
        'modulo': modulo,
        'puo_modificare': True,
        'campagna': campagna,
    }
    return 'donazioni_campagna_modifica.html', contesto


@pagina_privata
def campagna_elimina(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    campagna.delete()
    return redirect(reverse('donazioni_campagne'))


@pagina_privata
def campagna(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, LETTURA):
        return redirect(ERRORE_PERMESSI)
    puo_modificare = me.permessi_almeno(campagna, MODIFICA)
    contesto = {
        'campagna': campagna,
        'puo_modificare': puo_modificare,
    }
    return 'donazioni_campagna_scheda_informazioni.html', contesto


@pagina_privata
def campagna_fine(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)

    if not me.permessi_almeno(campagna, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in campagna.responsabili_attuali:  # Se sono responsabile
        redirect(campagna.url)

    contesto = {
        'campagna': campagna,
    }
    return 'donazioni_campagna_fine.html', contesto


@pagina_privata
def campagna_responsabili(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    continua_url = campagna.url

    if 'campagna_creata' in request.session and int(request.session['campagna_creata']) == int(pk):
        continua_url = "/donazioni/campagne/%d/fine/" % (int(pk),)
        del request.session['campagna_creata']

    contesto = {
        'delega': RESPONSABILE_CAMPAGNA,
        'campagna': campagna,
        'continua_url': continua_url,
        'puo_modificare': True,
    }

    return 'donazioni_campagna_responsabili.html', contesto


# ######## ETICHETTE #################

@pagina_privata
def etichetta(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)
    if not me.permessi_almeno(etichetta, LETTURA):
        return redirect(ERRORE_PERMESSI)

    contesto = {
        'etichetta': etichetta,
        'puo_modificare': me.permessi_almeno(etichetta, COMPLETO),
    }
    return 'donazioni_etichetta_scheda.html', contesto


@pagina_privata
def etichetta_nuova(request, me):
    if not me.ha_permesso(GESTIONE_CAMPAGNA):
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloEtichetta(request.POST or None)

    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect(reverse('donazioni_etichetta', args=(etichetta.pk,)))

    contesto = {
        'modulo': modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata
def etichetta_modifica(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)
    if not me.permessi_almeno(etichetta, MODIFICA) or etichetta.default:
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloEtichetta(request.POST or None, instance=etichetta)
    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect(reverse('donazioni_etichetta', args=(etichetta.pk,)))
    contesto = {
        'modulo': modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata
def etichetta_elimina(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)
    if not me.permessi_almeno(etichetta, COMPLETO) or etichetta.default:
        return redirect(ERRORE_PERMESSI)
    etichetta.delete()
    return redirect(reverse('donazioni_etichette'))


@pagina_privata
def etichette_elenco(request, me):
    comitati = me.sedi_attuali().values_list('id', flat=True)
    sedi_deleghe_campagne = me.oggetti_permesso(GESTIONE_CAMPAGNE).values_list('id', flat=True)
    campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    filtro_etichette = Q(comitato__in=chain(comitati, sedi_deleghe_campagne)) | Q(campagne__in=campagne_qs)
    elenco = ElencoEtichette(Etichetta.objects.filter(filtro_etichette).distinct())
    contesto = {
        'puo_creare': me.ha_permesso(GESTIONE_CAMPAGNA),
        'elenco': elenco,
    }
    return 'donazioni_etichette_elenco.html', contesto


# ######## DONAZIONI #########


@pagina_privata
def donazione(request, me, pk):
    donazione = get_object_or_404(Donazione.objects.select_related('donatore'), pk=pk)
    if not me.permessi_almeno(donazione, LETTURA):
        return redirect(ERRORE_PERMESSI)

    contesto = {
        'donazione': donazione,
        'puo_modificare': me.permessi_almeno(donazione, MODIFICA),
        'puo_eliminare': me.permessi_almeno(donazione, COMPLETO),
    }
    return 'donazioni_donazione_scheda.html', contesto


@pagina_privata
def donazione_modifica(request, me, pk):
    donazione = get_object_or_404(Donazione, pk=pk)
    if not me.permessi_almeno(donazione, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo_donazione = ModuloDonazione(request.POST or None, instance=donazione, campagna=donazione.campagna_id)
    if modulo_donazione.is_valid():
        donazione = modulo_donazione.save()
        return redirect(reverse('donazioni_donazione', args=(pk, )))

    donatore = donazione.donatore
    contesto = {
        'modulo': modulo_donazione,
        'donatore': donatore,
        'puo_modificare': me.permessi_almeno(donazione, MODIFICA),
        'puo_modificare_donatore': me.permessi_almeno(donatore, MODIFICA),
    }
    return 'donazioni_donazione_modifica.html', contesto


@pagina_privata
def donazione_elimina(request, me, pk):
    donazione = get_object_or_404(Donazione, pk=pk)
    campagna = donazione.campagna
    if not me.permessi_almeno(donazione, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    donazione.delete()
    return redirect(reverse('donazioni_campagne_donazioni', args=(campagna.id,)))


@pagina_privata
def donazione_nuova(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not campagna.iniziata:
        messages.add_message(request, messages.WARNING, 'Non è possibile aggiungere donazioni prima della data di inizio della campagna.')
        return redirect(campagna.url)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    modulo_donazione = ModuloDonazione(request.POST or None, campagna=campagna_id)
    modulo_donatore = ModuloDonatore(request.POST or None, nuova_donazione=True)

    if not modulo_donazione.is_valid() or (modulo_donatore.has_changed() and not modulo_donatore.is_valid()):
        contesto = {
            'modulo_donazione': modulo_donazione,
            'modulo_donatore': modulo_donatore,
            'puo_modificare': True,
            'campagna': campagna,
        }
        return 'donazioni_donazione_nuova.html', contesto

    if modulo_donazione.is_valid():
        donazione = modulo_donazione.save(commit=False)
        messaggio_debug = ''
        if modulo_donatore.has_changed() and modulo_donatore.is_valid():
            donatore = Donatore.nuovo_o_esistente(modulo_donatore.instance)
            if donazione.modalita_singola_ricorrente == Donazione.RICORRENTE:
                donatore.periodico = True
                donatore.save()
            donazione.donatore = donatore
            if donatore.email and modulo_donatore.cleaned_data['invia_email']:
                registrazione_donatore_persona = AssociazioneDonatorePersona.objects.filter(donatore=donatore).first() or None
                if registrazione_donatore_persona:
                    # registrazione per il donatore già effettuata. Aggiungi appartenenza a Sede se non esistente
                    p = registrazione_donatore_persona.persona
                    sede = campagna.organizzatore
                    tipo_appartenenza = Appartenenza.SOGGETTO_DONATORE
                    if not Appartenenza.objects.filter(persona=p, sede=sede, membro=tipo_appartenenza).exists():
                        a = Appartenenza(
                            confermata=True,
                            persona=p,
                            inizio=poco_fa(),
                            sede=sede,
                            membro=tipo_appartenenza,
                        )
                        a.save()
                link_debug = invia_mail_ringraziamento(donatore, campagna, registrazione_donatore_persona)
                donazione.email_inviata = True
                messaggio_debug = ' <br/> DEBUG: link registrazione donatore <a href="{}">{}</a>'.format(link_debug, link_debug)

        donazione.save()
        messaggio = 'Donazione aggiunta con successo: {:.2f} € donati da {}'.format(donazione.importo, donazione.donatore or 'Anonimo')
        if settings.DEBUG:
            messaggio += messaggio_debug
        messages.add_message(request, messages.SUCCESS, mark_safe(messaggio))
        return redirect(reverse('donazioni_campagne_donazioni', args=(campagna_id,)))


@pagina_privata
def donazione_ricevuta(request, me, pk):
    donazione = get_object_or_404(Donazione, pk=pk)
    donatore = donazione.donatore

    filtro_persona = Q(donatore=donatore)
    if not me.permessi_almeno(donazione, COMPLETO):
        # L'utente che sta cercando di scaricare la ricevuta non è un responsabile di campagna
        # quindi è un utente registrato. Verificare se è il donatore stesso
        filtro_persona = Q(persona=me, donatore=donatore)

    try:
        persona = AssociazioneDonatorePersona.objects.get(filtro_persona).persona
    except AssociazioneDonatorePersona.DoesNotExist:
        # l'utente sta cercando di scaricare una ricevuta di un altro utente
        # oppure quella di un donatore non registrato
        return redirect(ERRORE_PERMESSI)

    campagna = donazione.campagna
    appartenenza = persona.appartenenze_attuali(
        sede=campagna.organizzatore, membro=Appartenenza.SOGGETTO_DONATORE
    ).first()
    ricevuta = donazione.ricevuta(appartenenza)
    if not ricevuta:
        ricevuta = Quota.nuova(
            appartenenza=appartenenza,
            data_versamento=donazione.data,
            registrato_da=campagna.organizzatore.presidente(),
            importo=donazione.importo,
            causale='Ricevuta donazione per campagna %s' % campagna,
            tipo=Quota.RICEVUTA_DONAZIONE,
            invia_notifica=True,
        )
    pdf = ricevuta.genera_pdf()
    return redirect(pdf.download_url)


@pagina_privata
def donazione_invia_notifica(request, me, pk):
    donazione = get_object_or_404(Donazione, pk=pk)
    if not me.permessi_almeno(donazione, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    if not donazione.donatore or not donazione.donatore.email:
        messages.add_message(request, messages.WARNING, 'La donazione non ha un donatore o il donatore non ha inserito un indirizzo email')
        return redirect(reverse('donazioni_campagne_donazioni', args=(donazione.campagna_id,)))

    modulo_invia_notifica = ModuloInviaNotifica(request.POST or None)
    if modulo_invia_notifica.is_valid():
        if not modulo_invia_notifica.cleaned_data['invia']:
            messages.add_message(request, messages.WARNING, 'Notifica non inviata')
            return redirect(reverse('donazioni_campagne_donazioni', args=(donazione.campagna_id,)))
        message, ok = invia_notifica_donatore(donazione)
        if ok:
            donazione.email_inviata = True
            donazione.save()
        messages.add_message(request, messages.SUCCESS if ok else messages.WARNING, message)
        return redirect(reverse('donazioni_campagne_donazioni', args=(donazione.campagna_id,)))
    contesto = {
        'modulo': modulo_invia_notifica,
        'donazione': donazione,
        'donatore': donazione.donatore,
    }
    return 'donazioni_donatore_invia_notifica.html', contesto


@pagina_privata
def donazioni_elenco(request, me, campagna_id):
    campagna = get_object_or_404(Campagna.objects.prefetch_related('donazioni', 'donazioni__donatore'), pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    elenco = ElencoDonazioni(campagna.donazioni.all().select_related('donatore', 'campagna'))
    contesto = {
        'campagna': campagna,
        'elenco': elenco,
        'puo_modificare': True,
    }
    return 'donazioni_campagna_elenco_donazioni.html', contesto


# ######## DONATORI #########


@pagina_privata
def donatore(request, me, pk):
    donatore = get_object_or_404(Donatore.objects.prefetch_related(
        'donazioni', 'etichette'),
        pk=pk)
    if not me.permessi_almeno(donatore, LETTURA):
        return redirect(ERRORE_PERMESSI)
    contesto = {
        'donatore': donatore,
    }
    return 'donazioni_donatore_scheda_informazioni.html', contesto


@pagina_privata
def donatore_modifica(request, me, pk):
    donatore = get_object_or_404(Donatore, pk=pk)
    if not me.permessi_almeno(donatore, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo_donatore = ModuloDonatore(request.POST or None, instance=donatore)
    if modulo_donatore.is_valid():
        donatore = modulo_donatore.save()
        return redirect(reverse('donazioni_donatore', args=(pk, )))

    contesto = {
        'donatore': donatore,
        'modulo': modulo_donatore,
    }
    return 'donazioni_donatore_modifica.html', contesto


@pagina_privata
def donatore_elimina(request, me, pk):
    donatore = get_object_or_404(Donatore, pk=pk)
    if not me.permessi_almeno(donatore, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    donatore.delete()
    return redirect(reverse('donazioni_campagne_donatori_elenco'))


@pagina_privata
def iframe_donatori_elenco(request, me, elenco_id=None, pagina=1):

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    try:
        elenco = request.session["donatori_elenco_%s" % (elenco_id,)]

    except KeyError:
        return errore_generico(request, me, titolo="Sessione scaduta",
                               messaggio="Ricarica la pagina.",
                               torna_url=request.path, torna_titolo="Riprova")

    if request.POST:
        request.session["donatori_elenco_filtra_%s" % (elenco_id,)] = request.POST['filtra']
        request.session["donatori_elenco_filtra_scaglione_%s" % (elenco_id,)] = request.POST['media']
        return redirect("/donazioni/donatori/ifrelenco/%s/%d/" % (elenco_id, 1))

    filtra = request.session.get("donatori_elenco_filtra_%s" % (elenco_id,), default="")
    scaglione_media = request.session.get("donatori_elenco_filtra_scaglione_%s" % (elenco_id,), default="")
    pagina_precedente = "/donazioni/donatori/ifrelenco/%s/%d/" % (elenco_id, pagina-1)
    pagina_successiva = "/donazioni/donatori/ifrelenco/%s/%d/" % (elenco_id, pagina+1)
    risultati = elenco.risultati()

    if filtra or scaglione_media:
        risultati = elenco.filtra(risultati, filtra, scaglione_media=scaglione_media)
    p = Paginator(risultati, 15)
    pg = p.page(pagina)
    scaglioni_media_filtro = settings.SCAGLIONI_MEDIA_DONAZIONE
    contesto = {
        'pagina': pagina,
        'pagine': p.num_pages,
        'totale': p.count,
        'risultati': pg.object_list,
        'ha_precedente': pg.has_previous(),
        'ha_successivo': pg.has_next(),
        'pagina_precedente': pagina_precedente,
        'pagina_successiva': pagina_successiva,
        'elenco_id': elenco_id,
        'filtra': filtra,
        'scaglione_media': scaglione_media,
        'elenco': elenco,
        'scaglioni_media_filtro': scaglioni_media_filtro,
    }
    contesto.update(**elenco.kwargs)

    return elenco.template(), contesto


@pagina_privata
def donatori_campagna_elenco(request, me, campagna_id):
    """
    Elenco Donatori per la Campagna specificata da campagna_id
    """
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    donatori_ids = Donazione.objects.filter(campagna=campagna).distinct('donatore__id').values_list('donatore__id')
    donatori = Donatore.objects.filter(id__in=donatori_ids).prefetch_related('donazioni')
    elenco = ElencoDonatori(donatori)
    contesto = {
        'campagna': campagna,
        'elenco': elenco,
        'puo_modificare': True,
    }
    return 'donazioni_campagna_elenco_donatori.html', contesto


@pagina_privata
def donatore_donazioni_elenco(request, me, pk):
    """
        Elenco Donazioni del Donatore specificato da pk
    """
    donatore = get_object_or_404(Donatore.objects.prefetch_related('donazioni', 'donazioni__campagna'), pk=pk)
    if not me.permessi_almeno(donatore, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    elenco = ElencoDonazioni(donatore.donazioni.all())
    contesto = {
        'donatore': donatore,
        'elenco': elenco,
    }
    return 'donazioni_donatore_elenco_donazioni.html', contesto


@pagina_privata
def donatori_elenco(request, me):
    """
    Elenco di tutti i Donatori associati alle campagne in delega
    """
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    donatori = Donatore.objects.filter(donazioni__campagna__in=campagne)
    elenco = ElencoDonatori(donatori)
    contesto = {
        'elenco_donatori': True,
        'elenco': elenco,
    }
    return 'donatori_elenco.html', contesto


@pagina_privata
def donazioni_import(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if 'contenuto_file' in request.session:
        del request.session['contenuto_file']
    modulo = ModuloImportDonazioni()
    contesto = {
        'campagna': campagna,
        'modulo': modulo,
        'puo_modificare': True,
    }
    return 'donazioni_import.html', contesto


@pagina_privata
def donazioni_import_step_1(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloImportDonazioni(data=request.POST or None, files=request.FILES or None)
    contesto = {
        'campagna': campagna,
        'modulo': modulo,
        'puo_modificare': True,
    }
    if modulo.is_valid():
        file_xls = modulo.cleaned_data['file_da_importare']
        formato = modulo.cleaned_data['formato']
        intestazione = modulo.cleaned_data['righe_intestazione']
        delimitatore = modulo.cleaned_data['delimitatore_csv']
        sorgente = modulo.cleaned_data['sorgente']
        colonne_preview, contenuto_file = analizza_file_import(file_xls, intestazione=intestazione,
                                                               formato=formato, separatore_csv=delimitatore)
        request.session['contenuto_file'] = (colonne_preview, contenuto_file, intestazione, sorgente)
        modulo_mapping_campi = ModuloImportDonazioniMapping(colonne=colonne_preview, sorgente=sorgente)
        contesto['modulo_mapping'] = modulo_mapping_campi
        contesto.pop('modulo')
    return 'donazioni_import.html', contesto


@pagina_privata
def donazioni_import_step_2(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    colonne_preview, contenuto_file, intestazione, sorgente = request.session.get('contenuto_file')
    if not contenuto_file:
        return redirect(reverse('donazioni_campagna_importa', args=(campagna_id,)))

    modulo = ModuloImportDonazioniMapping(data=request.POST or None,
                                          colonne=colonne_preview,
                                          intestazione=intestazione,
                                          sorgente=sorgente)
    contesto = {
        'campagna': campagna,
        'modulo_mapping': modulo,
        'puo_modificare': True,
    }

    if modulo.is_valid():
        test_importazione = 'test_import' in request.POST
        riepilogo = modulo.processa(campagna, contenuto_file, test_import=test_importazione)
        contesto['riepilogo_errori'] = riepilogo['errori']

        riepilogo_messaggio = '{}<br />' \
                              '<br /><strong>Donazioni Inserite: {} ' \
                              '<br /><strong>Donatori Inseriti: {} ' \
                              '<br />Righe con errori: {}</strong>'\
            .format('<span class="badge">TEST di Importazione</span>' if test_importazione else '',
                    len(riepilogo['donazioni_inserite']),
                    len(riepilogo['donatori_inseriti']),
                    len(riepilogo['non_inserite']))

        if riepilogo['inserite_incomplete']:
            riepilogo_messaggio += '<br/ >Donazioni inserite ma con valori non conformi: {}'.format(len(riepilogo['inserite_incomplete']))

        if not test_importazione:
            del request.session['contenuto_file']
            messages.add_message(request, messages.WARNING, mark_safe(riepilogo_messaggio), extra_tags='email')
            return redirect(reverse('donazioni_campagne_donazioni', args=(campagna_id,)))

        contesto['riepilogo_messaggio'] = riepilogo_messaggio

    return 'donazioni_import.html', contesto


@pagina_privata
def donatori_importa_mailup(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    sede = campagna.organizzatore
    account = sede.mailup
    if not account:
        messages.add_message(request, messages.ERROR, "Il comitato organizzatore non ha configurato l'account MailUp")
        return redirect(reverse('donazioni_campagne_donazioni', args=(campagna_id,)))
    liste = account.liste()
    modulo = ModuloImportaMailUp(request.POST or None, liste=liste)
    if modulo.is_valid():
        nuovi_contatti = []
        campagna_fittizia = SedeCampagnaFittizia.ottieni_campagna_fittizia(sede=campagna.organizzatore, campagna=campagna)
        for id_lista in modulo.cleaned_data['liste']:
            contatti = account.contatti(id_lista)

            for c in contatti:
                donatore = Donatore(**c)
                esiste_gia, istanza = Donatore.esiste_gia(donatore)
                # import di profilo donatore senza donazioni: associazione a campagna fittizia
                if esiste_gia:
                    continue
                donatore.save()
                nome_lista = [l[1] for l in liste if l[0] == int(id_lista)][0]
                etichetta = Etichetta(slug=slugify(nome_lista), comitato=sede)
                etichetta.save()
                donatore.etichette.add(etichetta)
                nuovi_contatti.append(donatore)
                donazione_fittizia = Donazione(importo=0, campagna=campagna_fittizia, donatore=donatore,
                                               data=poco_fa(), permetti_scaricamento_ricevute=False,
                                               )
                donazione_fittizia.save()
        messages.add_message(request, messages.SUCCESS, 'Importati {} nuovi contatti'.format(len(nuovi_contatti)))
        return redirect(reverse('donazioni_campagne_donatori_elenco'))

    contesto = {
        'campagna': campagna,
        'modulo': modulo,
    }
    return 'donazioni_import_mailup.html', contesto


@pagina_privata
def autocompletamento_etichette(request, me):
    """
    Vista AJAX per autocompletamento etichette nel filtro di Elenco Campagne
    """
    term = request.GET.get('term')
    comitati = me.sedi_attuali().values_list('id', flat=True)
    sedi_deleghe_campagne = me.oggetti_permesso(GESTIONE_CAMPAGNE).values_list('id', flat=True)
    campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    filtro_etichette = Q(comitato__in=chain(comitati, sedi_deleghe_campagne)) | Q(campagne__in=campagne_qs)
    etichette = Etichetta.objects.filter(filtro_etichette).filter(slug__icontains=term).distinct('slug').values_list('slug', flat=True)
    return JsonResponse(list(etichette), safe=False)


@pagina_pubblica
def modulo_mailup(request, me=None, campagna_id=None):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    id_lista_mailup = campagna.id_lista_mailup or None
    if not id_lista_mailup:
        redirect(ERRORE_ORFANO)

    contesto = {
        'campagna': campagna,
        'lista': id_lista_mailup
    }

    if request.POST:
        id_lista = request.POST['id_lista']
        if id_lista != id_lista_mailup:
            redirect(ERRORE_PERMESSI)

        email = request.POST['email']
        nome = request.POST.get('nome')
        telefono = request.POST.get('telefono')

        res = iscrivi_email(campagna, id_lista_mailup, nome, email, telefono)
        if res:
            contesto['successo'] = True

    return 'modulo_mailup.html', contesto


@pagina_privata
def statistiche_elenco_campagne(request, me, elenco_id):
    try:
        elenco = request.session['elenco_%s' % elenco_id]
    except KeyError:  # Se l'elenco non e' piu' in sessione, potrebbe essere scaduto.
        raise ValueError("Elenco non presente in sessione.")

    # Eventuale termine di ricerca
    filtra = request.session.get("elenco_filtra_%s" % (elenco_id,), default="")

    campagne = elenco.ordina(elenco.risultati())
    if filtra:  # Filtra risultati per etichette
        campagne = elenco.filtra(campagne, filtra)

    donatori = Donatore.objects.filter(donazioni__campagna__in=campagne).distinct('id')
    donazioni = Donazione.objects.filter(campagna__in=campagne).order_by('data')

    donazioni_mese_anno = donazioni_per_mese_anno(donazioni)
    donazioni_per_settimana, donazioni_per_settimana_xls = donazioni_chart_52_settimane(donazioni)
    fondi_raccolti = donazioni.aggregate(totale=Sum('importo'))
    if request.POST:
        excel = Excel(oggetto=me)
        fogli = {'Riepilogo': FoglioExcel('Riepilogo', ['']),
                 'Statistiche mese anno': FoglioExcel('Statistiche mese anno', ['Mese/Anno', '# Donazioni', 'Importo']),
                 'Statistiche ultime 52 settimane': FoglioExcel('Statistiche ultime 52 settimane', ['# Settimana', '# Donazioni', 'Importo'])}
        # Riepilogo
        fogli['Riepilogo'].aggiungi_riga('Numero campagne', campagne.count())
        if filtra:
            fogli['Riepilogo'].aggiungi_riga('Filtro etichette applicato', filtra)

        fogli['Riepilogo'].aggiungi_riga('Numero totale donazioni', donazioni.count())
        fogli['Riepilogo'].aggiungi_riga('Numero totale donatori', donatori.count())
        fogli['Riepilogo'].aggiungi_riga('Totale economico donazioni', '{} €'.format(fondi_raccolti['totale']))
        for mese_anno, valori in donazioni_mese_anno.items():
            mese = mese_anno[0]
            anno = mese_anno[1]
            fogli['Statistiche mese anno'].aggiungi_riga('{}/{}'.format(mese, anno), valori['count'], '{} €'.format(valori['totale']))
        for settimana, valori in donazioni_per_settimana_xls.items():
            fogli['Statistiche ultime 52 settimane'].aggiungi_riga(settimana, valori['count'], '{} €'.format(valori['totale']))
        excel.fogli = fogli.values()
        excel.genera_e_salva(nome='Statistiche_Donazioni.xlsx')
        return redirect(excel.download_url)

    contesto = {'elenco_id': elenco_id, 'campagne': campagne, 'filtra': filtra,
                'donazioni': donazioni, 'donazioni_mese_anno': donazioni_mese_anno,
                'chart': donazioni_per_settimana,
                'donatori': donatori, 'fondi_raccolti': fondi_raccolti}
    return 'donazioni_statistiche_campagne.html', contesto




