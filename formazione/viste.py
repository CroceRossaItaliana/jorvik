from datetime import datetime, timedelta

# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.transaction import atomic
# from django.template import Context
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.loader import get_template

from anagrafica.models import Persona
from anagrafica.permessi.applicazioni import DIRETTORE_CORSO
from anagrafica.permessi.costanti import (GESTIONE_CORSI_SEDE,
    GESTIONE_CORSO, ERRORE_PERMESSI, COMPLETO, MODIFICA)
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico, messaggio_generico # ci_siamo_quasi
from base.files import Zip
from base.models import Log
from base.utils import poco_fa
from posta.models import Messaggio
from .elenchi import ElencoPartecipantiCorsiBase
from .decorators import access_to_courses
from .models import (Corso, CorsoBase, CorsoEstensione, AssenzaCorsoBase,
    LezioneCorsoBase, PartecipazioneCorsoBase, Aspirante, InvitoCorsoBase)
from .forms import (ModuloCreazioneCorsoBase, ModuloModificaLezione,
    ModuloModificaCorsoBase, ModuloIscrittiCorsoBaseAggiungi,
    ModuloVerbaleAspiranteCorsoBase)


@pagina_privata
def formazione(request, me):
    contesto = {
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
        "corsi": me.oggetti_permesso(GESTIONE_CORSO),
    }
    return 'formazione.html', contesto


@pagina_privata
def formazione_corsi_base_elenco(request, me):
    contesto = {
        "corsi": me.oggetti_permesso(GESTIONE_CORSO),
        "puo_pianificare": me.ha_permesso(GESTIONE_CORSI_SEDE),
    }
    return 'formazione_corsi_base_elenco.html', contesto


@pagina_privata
def formazione_corsi_base_domanda(request, me):
    contesto = {
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
        "min_sedi": Aspirante.MINIMO_COMITATI,
        "max_km": Aspirante.MASSIMO_RAGGIO,
    }
    return 'formazione_corsi_base_domanda.html', contesto


@pagina_privata
def formazione_corsi_base_nuovo(request, me):
    data_inizio = datetime.now() + timedelta(days=14)
    form = ModuloCreazioneCorsoBase(
        request.POST or None, initial={"data_inizio": data_inizio}
    )
    form.fields['sede'].queryset = me.oggetti_permesso(GESTIONE_CORSI_SEDE)

    if form.is_valid():
        cd = form.cleaned_data
        course = CorsoBase.nuovo(
            anno=cd['data_inizio'].year,
            sede=cd['sede'],
            data_inizio=cd['data_inizio'],
            data_esame=cd['data_inizio'],
        )

        if cd['locazione'] == form.PRESSO_SEDE:
            course.locazione = course.sede.locazione
            course.save()

        request.session['corso_base_creato'] = course.pk
        return redirect(course.url_direttori)

    context = {
        'modulo': form
    }
    return 'formazione_corsi_base_nuovo.html', context


@pagina_privata
def formazione_corsi_base_direttori(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    continua_url = corso.url

    if 'corso_base_creato' in request.session and int(request.session['corso_base_creato']) == int(pk):
        continua_url = "/formazione/corsi-base/%d/fine/" % (int(pk),)
        del request.session['corso_base_creato']

    contesto = {
        "delega": DIRETTORE_CORSO,
        "corso": corso,
        "continua_url": continua_url
    }
    return 'formazione_corsi_base_direttori.html', contesto


@pagina_privata
def formazione_corsi_base_fine(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in corso.delegati_attuali():  # Se sono direttore, continuo.
        redirect(corso.url)

    contesto = {
        "corso": corso,
    }
    return 'formazione_corsi_base_fine.html', contesto


@pagina_pubblica
def aspirante_corso_base_informazioni(request, me=None, pk=None):
    corso = get_object_or_404(CorsoBase, pk=pk)
    puo_modificare = me and me.permessi_almeno(corso, MODIFICA)
    puoi_partecipare = corso.persona(me) if me else None

    contesto = {
        "corso": corso,
        "puo_modificare": puo_modificare,
        "puoi_partecipare": puoi_partecipare,
    }
    return 'aspirante_corso_base_scheda_informazioni.html', contesto


@pagina_privata
def aspirante_corso_base_iscriviti(request, me=None, pk=None):

    corso = get_object_or_404(CorsoBase, pk=pk)
    puoi_partecipare = corso.persona(me)
    if not puoi_partecipare in corso.PUOI_ISCRIVERTI:
        return errore_generico(request, me, titolo="Non puoi partecipare a questo corso",
                               messaggio="Siamo spiacenti, ma non sembra che tu possa partecipare "
                                         "a questo corso per qualche motivo. ",
                               torna_titolo="Torna al corso",
                               torna_url=corso.url)

    p = PartecipazioneCorsoBase(persona=me, corso=corso)
    p.save()
    p.richiedi()
    return messaggio_generico(request, me, titolo="Sei iscritto al corso base",
                              messaggio="Complimenti! Abbiamo inoltrato la tua richiesta al direttore "
                                        "del corso, che ti contatterà appena possibile.",
                              torna_titolo="Torna al corso",
                              torna_url=corso.url)


@pagina_privata
def aspirante_corso_base_ritirati(request, me=None, pk=None):

    corso = get_object_or_404(CorsoBase, pk=pk)
    puoi_partecipare = corso.persona(me)
    if not puoi_partecipare == corso.SEI_ISCRITTO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirarti da questo corso",
                               messaggio="Siamo spiacenti, ma non sembra che tu possa ritirarti "
                                         "da questo corso per qualche motivo. ",
                               torna_titolo="Torna al corso",
                               torna_url=corso.url)

    p = PartecipazioneCorsoBase.con_esito_pending(corso=corso, persona=me).first()
    p.ritira()

    return messaggio_generico(request, me, titolo="Ti sei ritirato dal corso",
                              messaggio="Siamo spiacenti che hai deciso di ritirarti da questo corso. "
                                        "La tua partecipazione è stata ritirata correttamente. "
                                        "Non esitare a iscriverti a questo o un altro corso, nel caso cambiassi idea.",
                              torna_titolo="Torna alla pagina del corso",
                              torna_url=corso.url)


@pagina_privata
def aspirante_corso_base_mappa(request, me, pk):

    corso = get_object_or_404(CorsoBase, pk=pk)
    puo_modificare = me.permessi_almeno(corso, MODIFICA)
    contesto = {
        "corso": corso,
        "puo_modificare": puo_modificare
    }
    return 'aspirante_corso_base_scheda_mappa.html', contesto


@pagina_privata
def aspirante_corso_base_lezioni(request, me, pk):

    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    partecipanti = Persona.objects.filter(partecipazioni_corsi__in=corso.partecipazioni_confermate())
    lezioni = corso.lezioni.all()
    moduli = []
    partecipanti_lezioni = []
    for lezione in lezioni:
        modulo = ModuloModificaLezione(request.POST if request.POST and request.POST['azione'] == 'salva' else None,
                                         instance=lezione,
                                         prefix="%s" % (lezione.pk,))
        if request.POST and request.POST['azione'] == 'salva' and modulo.is_valid():
            modulo.save()

        moduli += [modulo]
        partecipanti_lezione = partecipanti.exclude(assenze_corsi_base__lezione=lezione).order_by('nome', 'cognome')

        if request.POST and request.POST['azione'] == 'salva':
            for partecipante in partecipanti:
                if ("%s" % (partecipante.pk,)) in request.POST.getlist('presenze-%s' % (lezione.pk,)):
                    # Se presente, rimuovi ogni assenza.
                    AssenzaCorsoBase.objects.filter(lezione=lezione, persona=partecipante).delete()
                else:
                    # Assicurati che sia segnato come assente.
                    if not AssenzaCorsoBase.objects.filter(lezione=lezione, persona=partecipante).exists():
                        a = AssenzaCorsoBase(lezione=lezione, persona=partecipante, registrata_da=me)
                        a.save()

        partecipanti_lezioni += [partecipanti_lezione]

    if request.POST and request.POST['azione'] == 'nuova':
        modulo_nuova_lezione = ModuloModificaLezione(request.POST, prefix="nuova")
        if modulo_nuova_lezione.is_valid():
            lezione = modulo_nuova_lezione.save(commit=False)
            lezione.corso = corso
            lezione.save()
            return redirect("%s#%d" % (corso.url_lezioni, lezione.pk,))
    else:
        modulo_nuova_lezione = ModuloModificaLezione(prefix="nuova", initial={
            "inizio": timezone.now(),
            "fine": timezone.now() + timedelta(hours=2)
        })


    lezioni = zip(lezioni, moduli, partecipanti_lezioni)

    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "lezioni": lezioni,
        "partecipanti": partecipanti,
        "modulo_nuova_lezione": modulo_nuova_lezione,
    }
    return 'aspirante_corso_base_scheda_lezioni.html', contesto


@pagina_privata
def aspirante_corso_base_lezioni_cancella(request, me, pk, lezione_pk):

    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    lezione = get_object_or_404(LezioneCorsoBase, pk=lezione_pk)
    if lezione.corso != corso:
        return redirect(ERRORE_PERMESSI)

    lezione.delete()
    return redirect(corso.url_lezioni)


@pagina_privata
def aspirante_corso_base_modifica(request, me, pk):
    from .models import CorsoFile, CorsoLink
    from .forms import CorsoFileFormSet, CorsoLinkFormSet

    course = get_object_or_404(CorsoBase, pk=pk)
    course_files = CorsoFile.objects.filter(corso=course)
    course_links = CorsoLink.objects.filter(corso=course)

    FILEFORM_PREFIX = 'files'
    LINKFORM_PREFIX = 'links'

    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if request.method == 'POST':
        course_form = ModuloModificaCorsoBase(request.POST, instance=course)
        file_formset = CorsoFileFormSet(request.POST, request.FILES,
                                        queryset=course_files,
                                        form_kwargs={'empty_permitted': False},
                                        prefix=FILEFORM_PREFIX)
        link_formset = CorsoLinkFormSet(request.POST,
                                        queryset=course_links,
                                        prefix=LINKFORM_PREFIX)

        if course_form.is_valid():
            course_form.save()

        if file_formset.is_valid():
            file_formset.save(commit=False)

            for obj in file_formset.deleted_objects:
                obj.delete()

            for form in file_formset:
                if form.is_valid() and not form.empty_permitted:
                    instance = form.instance
                    instance.corso = course
            file_formset.save()

        if link_formset.is_valid():
            link_formset.save(commit=False)
            for form in link_formset:
                instance = form.instance
                instance.corso = course
            link_formset.save()

        return redirect(reverse('aspirante:modify', args=[pk]))
    else:
        course_form = ModuloModificaCorsoBase(instance=course)
        file_formset = CorsoFileFormSet(queryset=course_files, prefix=FILEFORM_PREFIX)
        link_formset = CorsoLinkFormSet(queryset=course_links, prefix=LINKFORM_PREFIX)

    context = {
        'corso': course,
        'puo_modificare': True,
        'modulo': course_form,
        'file_formset': file_formset,
        'link_formset': link_formset,
    }
    return 'aspirante_corso_base_scheda_modifica.html', context


@pagina_privata
def aspirante_corso_base_attiva(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if corso.stato != corso.PREPARAZIONE:
        return messaggio_generico(request, me, titolo="Il corso è già attivo",
                                  messaggio="Non puoi attivare un corso già attivo",
                                  torna_titolo="Torna al Corso",
                                  torna_url=corso.url)
    if not corso.attivabile():
        return errore_generico(request, me, titolo="Impossibile attivare questo corso",
                               messaggio="Non sono soddisfatti tutti i criteri di attivazione. "
                                         "Torna alla pagina del corso e verifica che tutti i "
                                         "criteri siano stati soddisfatti prima di attivare un "
                                         "nuovo corso.",
                               torna_titolo="Torna al Corso",
                               torna_url=corso.url)

    if corso.data_inizio < poco_fa():
        return errore_generico(request, me, titolo="Impossibile attivare un corso già iniziato",
                               messaggio="Siamo spiacenti, ma non possiamo attivare il corso e inviare "
                                         "le e-mail a tutti gli aspiranti nella zona se il corso è "
                                         "già iniziato. Ti inviato a verificare i dati del corso.",
                               torna_titolo="Torna al Corso",
                               torna_url=corso.url)

    corpo = {"corso": corso, "persona": me}
    testo = get_template("email_aspirante_corso_inc_testo.html").render(corpo)

    if request.POST:
        corso.attiva(rispondi_a=me)
        return messaggio_generico(request, me, titolo="Corso attivato con successo",
                                  messaggio="A breve tutti gli aspiranti nelle vicinanze verranno informati "
                                            "dell'attivazione di questo corso base.",
                                  torna_titolo="Torna al Corso",
                                  torna_url=corso.url)

    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "testo": testo,
    }
    return 'aspirante_corso_base_scheda_attiva.html', contesto


@pagina_privata
def aspirante_corso_base_termina(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    torna = {"torna_url": corso.url_modifica, "torna_titolo": "Modifica corso"}

    if (not corso.op_attivazione) or (not corso.data_attivazione):
        return errore_generico(request, me, titolo="Necessari dati attivazione",
                               messaggio="Per generare il verbale, sono necessari i dati (O.P. e data) "
                                         "dell'attivazione del corso.",
                               **torna)

    if not corso.partecipazioni_confermate().exists():
        return errore_generico(request, me, titolo="Impossibile terminare questo corso",
                               messaggio="Non ci sono partecipanti confermati per questo corso, "
                                         "non è quindi possibile generare un verbale per il corso.",
                               **torna)

    if corso.stato != corso.ATTIVO:
        return errore_generico(request, me, titolo="Impossibile terminare questo corso",
                               messaggio="Il corso non è attivo e non può essere terminato.",
                               **torna)

    partecipanti_moduli = []

    azione = request.POST.get('azione', default=ModuloVerbaleAspiranteCorsoBase.SALVA_SOLAMENTE)
    generazione_verbale = azione == ModuloVerbaleAspiranteCorsoBase.GENERA_VERBALE

    termina_corso = generazione_verbale

    for partecipante in corso.partecipazioni_confermate():

        modulo = ModuloVerbaleAspiranteCorsoBase(
            request.POST or None, prefix="part_%d" % partecipante.pk,
            instance=partecipante,
            generazione_verbale=generazione_verbale
        )
        modulo.fields['destinazione'].queryset = corso.possibili_destinazioni()
        modulo.fields['destinazione'].initial = corso.sede

        if modulo.is_valid():
            modulo.save()

        elif generazione_verbale:
            termina_corso = False

        partecipanti_moduli += [(partecipante, modulo)]

    if termina_corso:  # Se il corso può essere terminato.
        corso.termina(mittente=me)
        return messaggio_generico(request, me, titolo="Corso base terminato",
                                  messaggio="Il verbale è stato generato con successo. Tutti gli idonei "
                                            "sono stati resi volontari delle rispettive sedi.",
                                  torna_titolo="Vai al Report del Corso Base",
                                  torna_url=corso.url_report)

    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "partecipanti_moduli": partecipanti_moduli,
        "azione_genera_verbale": ModuloVerbaleAspiranteCorsoBase.GENERA_VERBALE,
        "azione_salva_solamente": ModuloVerbaleAspiranteCorsoBase.SALVA_SOLAMENTE,
    }
    return 'aspirante_corso_base_scheda_termina.html', contesto


@pagina_privata
def aspirante_corso_base_iscritti(request, me, pk):

    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    elenco = ElencoPartecipantiCorsiBase(corso.queryset_modello())
    in_attesa = corso.partecipazioni_in_attesa()
    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "elenco": elenco,
        "in_attesa": in_attesa,
    }
    return 'aspirante_corso_base_scheda_iscritti.html', contesto


@pagina_privata
def aspirante_corso_base_iscritti_cancella(request, me, pk, iscritto):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not corso.possibile_cancellare_iscritti:
        return errore_generico(request, me, titolo="Impossibile cancellare iscritti",
                               messaggio="Non si possono cancellare iscritti a questo "
                                         "stadio della vita del corso base.",
                               torna_titolo="Torna al corso base", torna_url=corso.url_iscritti)

    try:
        persona = Persona.objects.get(pk=iscritto)
    except Persona.DoesNotExist:
        return errore_generico(request, me, titolo="Impossibile cancellare iscritto",
                               messaggio="La persona cercata non è iscritta.",
                               torna_titolo="Torna al corso base", torna_url=corso.url_iscritti)
    if request.method == 'POST':
        for partecipazione in corso.partecipazioni_confermate_o_in_attesa().filter(persona=persona):
            partecipazione.disiscrivi(mittente=me)
        for partecipazione in corso.inviti_confermati_o_in_attesa().filter(persona=persona):
            partecipazione.disiscrivi(mittente=me)
        return messaggio_generico(request, me, titolo="Iscritto cancellato",
                                  messaggio="{} è stato cancellato dal corso {}.".format(persona, corso),
                                  torna_titolo="Torna al corso base", torna_url=corso.url_iscritti)
    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "persona": persona,
    }
    return 'aspirante_corso_base_scheda_iscritti_cancella.html', contesto


@pagina_privata
def aspirante_corso_base_iscritti_aggiungi(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not corso.possibile_aggiungere_iscritti:
        return errore_generico(request, me, titolo="Impossibile aggiungere iscritti",
                               messaggio="Non si possono aggiungere altri iscritti a questo "
                                         "stadio della vita del corso base.",
                               torna_titolo="Torna al corso base", torna_url=corso.url_iscritti)

    modulo = ModuloIscrittiCorsoBaseAggiungi(request.POST or None)
    risultati = []
    if modulo.is_valid():

        for persona in modulo.cleaned_data['persone']:
            esito = corso.persona(persona)
            ok = PartecipazioneCorsoBase.NON_ISCRITTO
            partecipazione = None

            if esito in corso.PUOI_ISCRIVERTI or esito in corso.NON_PUOI_ISCRIVERTI_SOLO_SE_IN_AUTONOMIA:
                if hasattr(persona, 'aspirante'):
                    inviti = InvitoCorsoBase.con_esito_ok() | InvitoCorsoBase.con_esito_pending()
                    if inviti.filter(persona=persona, corso=corso).exists():
                        ok = PartecipazioneCorsoBase.INVITO_INVIATO
                        partecipazione = InvitoCorsoBase.objects.filter(persona=persona, corso=corso).first()
                    else:
                        partecipazione = InvitoCorsoBase(persona=persona, corso=corso, invitante=me)
                        partecipazione.save()
                        partecipazione.richiedi()
                        ok = PartecipazioneCorsoBase.IN_ATTESA_ASPIRANTE
                else:
                    partecipazione = PartecipazioneCorsoBase.objects.create(persona=persona, corso=corso)
                    ok = PartecipazioneCorsoBase.ISCRITTO
                    Messaggio.costruisci_e_invia(
                        oggetto="Iscrizione a Corso Base",
                        modello="email_corso_base_iscritto.html",
                        corpo={
                            "persona": persona,
                            "corso": corso,
                        },
                        mittente=me,
                        destinatari=[persona]
                    )

                Log.crea(me, partecipazione)

            risultati += [{
                "persona": persona,
                "partecipazione": partecipazione,
                "esito": esito,
                "ok": ok,
            }]

    contesto = {
        "corso": corso,
        "puo_modificare": True,
        "modulo": modulo,
        "risultati": risultati,
    }
    return 'aspirante_corso_base_scheda_iscritti_aggiungi.html', contesto


@pagina_privata
def aspirante_corso_base_firme(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    archivio = corso.genera_pdf_firme()
    return redirect(archivio.download_url)


@pagina_privata
def aspirante_corso_base_report(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    contesto = {
        "corso": corso,
        "puo_modificare": True,
    }
    return 'aspirante_corso_base_scheda_report.html', contesto


@pagina_privata
def aspirante_corso_base_report_schede(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    archivio = Zip(oggetto=corso)
    for p in corso.partecipazioni_confermate():

        # Genera la scheda di valutazione.
        scheda = p.genera_scheda_valutazione()
        archivio.aggiungi_file(scheda.file.path, "%s - Scheda di Valutazione.pdf" % p.persona.nome_completo)

        # Se idoneo, genera l'attestato.
        if p.idoneo:
            attestato = p.genera_attestato()
            archivio.aggiungi_file(attestato.file.path, "%s - Attesato.pdf" % p.persona.nome_completo)

    archivio.comprimi_e_salva(nome="Corso %d-%d.zip" % (corso.progressivo, corso.anno))
    return redirect(archivio.download_url)


@pagina_privata
def aspirante_home(request, me):
    if not me.ha_aspirante:
        return redirect(ERRORE_PERMESSI)

    contesto = {}
    return 'aspirante_home.html', contesto


@pagina_privata
@access_to_courses
def aspirante_corsi(request, me):
    """ url: /aspirante/corsi/ """
    context = {
        'corsi': me.aspirante.corsi(),
    }
    return 'aspirante_corsi_base.html', context


@pagina_privata
def aspirante_sedi(request, me):
    if not me.ha_aspirante:
        return redirect(ERRORE_PERMESSI)

    contesto = {
        "sedi": me.aspirante.sedi(),
    }
    return 'aspirante_sedi.html', contesto


@pagina_privata
def aspirante_impostazioni(request, me):
    if not me.ha_aspirante:
        return redirect(ERRORE_PERMESSI)

    contesto = {}
    return 'aspirante_impostazioni.html', contesto


@pagina_privata
def aspirante_impostazioni_cancella(request, me):
    if not me.ha_aspirante:
        return redirect(ERRORE_PERMESSI)

    if not me.cancellabile:
        return errore_generico(request, me,
            titolo="Impossibile cancellare automaticamente il profilo da Gaia",
            messaggio="E' necessario richiedere la cancellazione manuale al personale di supporto."
        )

    # Cancella!
    me.delete()

    return messaggio_generico(request, me,
        titolo="Il tuo profilo è stato cancellato da Gaia",
        messaggio="Abbiamo rimosso tutti i tuoi dati dal nostro sistema. "
                "Se cambierai idea, non esitare a iscriverti nuovamente! "
    )


@pagina_privata
def aspirante_corso_estensioni_modifica(request, me, pk):
    from .forms import CorsoSelectExtensionTypeForm, CorsoSelectExtensionFormSet

    SELECT_EXTENSION_TYPE_FORM_PREFIX = 'extension_type'
    SELECT_EXTENSIONS_FORMSET_PREFIX = 'extensions'

    course = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not course.tipo == Corso.CORSO_NUOVO:
        # The page is not accessible if the type of course is not CORSO_NUOVO
        return redirect(ERRORE_PERMESSI)

    if request.method == 'POST':
        select_extension_type_form = CorsoSelectExtensionTypeForm(request.POST,
                                    instance=course,
                                    prefix=SELECT_EXTENSION_TYPE_FORM_PREFIX)
        select_extensions_formset = CorsoSelectExtensionFormSet(request.POST,
                                    prefix=SELECT_EXTENSIONS_FORMSET_PREFIX,
                                    form_kwargs={'corso': course})

        if select_extension_type_form.is_valid() and \
            select_extensions_formset.is_valid():
            select_extensions_formset.save(commit=False)

            for form in select_extensions_formset:
                if form.is_valid:
                    cd = form.cleaned_data
                    instance = form.save(commit=False)
                    instance.corso = course
                    corso = instance.corso

                    # Skip blank extra formset
                    if cd == {} and len(select_extensions_formset) >= 1:
                        continue

                    # Do validation only with specified extension type
                    if corso.extension_type == CorsoBase.EXT_LVL_REGIONALE:
                        msg = 'Questo campo è obbligatorio.'
                        if not cd.get('sede'):
                            form.add_error('sede', msg)
                        if not cd.get('segmento'):
                            form.add_error('segmento', msg)
                        if cd.get('sedi_sottostanti') and not cd.get('sede'):
                            form.add_error('sede', 'Seleziona una sede')

                    # No errors nor new added error - save form instance
                    if not form.errors:
                        instance.save()

            # Return form with error without saving
            if any(select_extensions_formset.errors):
                pass
            else:
                # Save all forms and redirect to the same page.
                select_extension_type_form.save()
                select_extensions_formset.save()
                return redirect(reverse('aspirante:estensioni_modifica', args=[pk]))

    else:
        select_extension_type_form = CorsoSelectExtensionTypeForm(
            prefix=SELECT_EXTENSION_TYPE_FORM_PREFIX,
            instance=course
        )
        select_extensions_formset = CorsoSelectExtensionFormSet(
            prefix=SELECT_EXTENSIONS_FORMSET_PREFIX,
            form_kwargs={'corso': course},
        )

    context = {
        'corso': course,
        'puo_modificare': True,
        'select_extension_type_form': select_extension_type_form,
        'select_extensions_formset': select_extensions_formset,
    }
    return 'aspirante_corso_estensioni_modifica.html', context
