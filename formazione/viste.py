from datetime import datetime, timedelta, date
from collections import OrderedDict

from django.db.models import Q, F
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.contrib import messages
from django.utils.timezone import now

from anagrafica.models import Persona, Documento, Sede
from anagrafica.forms import ModuloCreazioneDocumento
from anagrafica.permessi.applicazioni import (DIRETTORE_CORSO, RESPONSABILE_FORMAZIONE,
    COMMISSARIO, PRESIDENTE)
from anagrafica.costanti import NAZIONALE, REGIONALE, LOCALE
from anagrafica.permessi.costanti import (GESTIONE_CORSI_SEDE,
    GESTIONE_CORSO, ERRORE_PERMESSI, COMPLETO, MODIFICA, RUBRICA_DELEGATI_OBIETTIVO_ALL)
from curriculum.models import Titolo, TitoloPersonale
from ufficio_soci.elenchi import ElencoPerTitoliCorso
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico, messaggio_generico
from base.models import Log
from base.utils import poco_fa
from posta.models import Messaggio
from survey.models import Survey
from .elenchi import ElencoPartecipantiCorsiBase
from .decorators import can_access_to_course
from .models import (Aspirante, Corso, CorsoBase, CorsoEstensione, LezioneCorsoBase,
                     PartecipazioneCorsoBase, InvitoCorsoBase, RelazioneCorso)
from .forms import (ModuloCreazioneCorsoBase, ModuloModificaLezione,
    ModuloModificaCorsoBase, ModuloIscrittiCorsoBaseAggiungi, FormCommissioneEsame,
    FormVerbaleCorso, FormRelazioneDelDirettoreCorso)
from .classes import GeneraReport, GestioneLezioni
from .utils import costruisci_titoli
from .training_api import TrainingApi



@pagina_privata
def formazione(request, me):
    corsi = me.oggetti_permesso(GESTIONE_CORSO)

    # Filtra corsi by stato
    if request.GET.get('stato'):
        stato = request.GET.get('stato')
        # Verifica che modello ha lo stato impostato in get-request
        if stato in [i[0] for i in Corso.STATO]:
            filtered = corsi.filter(stato=stato)
            if not filtered.exists():  # queryset vuoto
                # Rindirizza sulla pagina con tutti i corsi disponibili
                return redirect('formazione:index')
            corsi = filtered

    context = {
        "corsi": corsi,
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
        "puo_pianificare": me.ha_permesso(GESTIONE_CORSI_SEDE),
    }
    return 'formazione.html', context


@pagina_privata
def formazione_osserva_corsi(request, me):
    context = dict()

    sedi = me.oggetti_permesso(GESTIONE_CORSI_SEDE)
    puo_accedere = set((NAZIONALE, REGIONALE)) & set([sede.estensione for sede in sedi])

    if not puo_accedere or not me.deleghe_attuali(tipo__in=[RESPONSABILE_FORMAZIONE, PRESIDENTE, COMMISSARIO]):
        messages.error(request, 'Non hai accesso a questa pagina.')
        return redirect('/formazione/')

    results = dict()
    def add_corsi_count_to_result(sede, comitato, corsi):
        if sede not in results:
            results[sede] = list()
        results[sede].append([comitato, corsi])

    sede_pk = request.GET.get('s')
    if sede_pk:
        try:
            sede = Sede.objects.get(pk=sede_pk)
        except ValueError:
            return redirect(reverse('formazione:osserva_corsi'))

        context['sede'] = sede
        context['corsi'] = CorsoBase.objects.filter(sede=sede)

        if sede.estensione in [NAZIONALE, REGIONALE,]:
            context['corsi'] = CorsoBase.objects.filter(sede__in=sede.comitati_sottostanti())
        else:
            context['corsi'] = CorsoBase.objects.filter(sede=sede)

    if not sede_pk:

        for sede in sedi:
            comitati = sede.comitati_sottostanti()

            if not comitati:  # GAIA-258
                corsi = CorsoBase.objects.filter(sede=sede).count()
                if sede not in results:
                    results[sede] = list()
                results[sede].append([sede, corsi])

            for comitato in comitati:
                if comitato.pk == 1663:  # Vila Maraini
                    continue

                if comitato.pk == 524:  # Lazio
                    # Area Metropolitana di Roma Capitale Coordinamento
                    roma_comitato = Sede.objects.get(pk=1638)
                    roma_corsi = CorsoBase.objects.filter(sede__in=roma_comitato.comitati_sottostanti()).count()
                    add_corsi_count_to_result(sede, roma_comitato, roma_corsi)

                if sede.estensione != REGIONALE:
                    comitati_sott_regione = comitato.comitati_sottostanti()
                    corsi = CorsoBase.objects.filter(sede__in=comitati_sott_regione).count()
                else:
                    corsi = CorsoBase.objects.filter(sede=comitato).count()

                if corsi:
                    add_corsi_count_to_result(sede, comitato, corsi)

        context['results'] = results

    return 'formazione_osserva_corsi.html', context


@pagina_privata
def formazione_corsi_base_elenco(request, me):
    puo_modificare = me.ha_permesso(GESTIONE_CORSI_SEDE)
    if not puo_modificare:
        return redirect(reverse('aspirante:corsi_base'))

    context = {
        "corsi": me.oggetti_permesso(GESTIONE_CORSO),
        "puo_pianificare": puo_modificare,
    }
    return 'formazione_corsi_base_elenco.html', context


@pagina_privata
def formazione_corsi_base_domanda(request, me):
    context = {
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
        "min_sedi": Aspirante.MINIMO_COMITATI,
        "max_km": Aspirante.MASSIMO_RAGGIO,
    }
    return 'formazione_corsi_base_domanda.html', context


@pagina_privata
def formazione_corsi_base_nuovo(request, me):
    if not me.ha_permesso(GESTIONE_CORSI_SEDE):
        return redirect(ERRORE_PERMESSI)

    now = datetime.now() + timedelta(days=14)
    form = ModuloCreazioneCorsoBase(
        request.POST or None,
        request.FILES or None,
        initial={'data_inizio': now, 'data_esame': now + timedelta(days=14)},
        me=me
    )
    form.fields['sede'].queryset = me.oggetti_permesso(GESTIONE_CORSI_SEDE)

    if form.is_valid():
        kwargs = {}
        cd = form.cleaned_data
        tipo, data_inizio, data_esame = cd['tipo'], cd['data_inizio'], cd['data_esame']
        # data_esame = data_esame if tipo == Corso.CORSO_NUOVO else data_inizio

        if tipo == Corso.BASE:
            # Impostare titolo per "Corso Base"
            kwargs['titolo_cri'] = Titolo.objects.get(sigla='CRI',
                                                      tipo=Titolo.TITOLO_CRI,
                                                      is_active=True)

        if tipo == Corso.CORSO_NUOVO or tipo == Corso.CORSO_ONLINE:
            kwargs['titolo_cri'] = cd['titolo_cri']
            kwargs['cdf_level'] = cd['level']
            kwargs['cdf_area'] = cd['area']

        course = CorsoBase.nuovo(
            anno=data_inizio.year,
            sede=cd['sede'],
            data_inizio=data_inizio,
            data_esame=data_esame,
            tipo=tipo,
            delibera_file=cd['delibera_file'],
            survey=Survey.survey_for_corso(),
            **kwargs
        )
        course.get_or_create_lezioni_precompilate()

        same_sede = cd['locazione'] == form.PRESSO_SEDE
        if same_sede:
            course.locazione = course.sede.locazione
            course.save()

        # Il corso è creato. Informa presidenza allegando delibera_file
        course.inform_presidency_with_delibera_file()
        request.session['corso_base_creato'] = course.pk
        online_sede = cd['locazione'] == form.ONLINE

        if same_sede or online_sede:
            # Rindirizza sulla pagina: selezione direttori
            return redirect(course.url_direttori)
        else:
            # Rindirizza sulla pagina: impostazione geolocalizzazione
            return redirect(reverse('aspirante:position_change', args=[course.pk]))

    context = {
        'modulo': form,
    }
    return 'formazione_corsi_base_nuovo.html', context


@pagina_privata
def formazione_corsi_base_direttori(request, me, pk):
    """
    La form con l'input di persone da nominare si trova carica con iframe da:
    url: /strumenti/delegati/
    view: anagrafica.viste.strumenti_delegati
    form: formazione.forms.FormCreateDirettoreDelega
    """

    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    continua_url = corso.url

    if 'corso_base_creato' in request.session and int(request.session['corso_base_creato']) == int(pk):
        continua_url = reverse('formazione:end', args=[pk])
        del request.session['corso_base_creato']

    context = {
        "delega": DIRETTORE_CORSO,
        "corso": corso,
        "continua_url": continua_url,
        'puo_modificare': me and me.permessi_almeno(corso, MODIFICA)
    }
    return 'formazione_corsi_base_direttori.html', context


@pagina_privata
def formazione_corsi_base_fine(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in corso.delegati_attuali():  # Se sono direttore, continuo.
        redirect(corso.url)

    context = {
        "corso": corso,
    }
    return 'formazione_corsi_base_fine.html', context


@pagina_pubblica
@can_access_to_course
def aspirante_corso_base_informazioni(request, me=None, pk=None):
    context = dict()
    corso = get_object_or_404(CorsoBase, pk=pk)
    puoi_partecipare = corso.persona(me) if me else None

    if corso.locazione is None and corso.tipo != Corso.CORSO_ONLINE:
        # Il corso non ha una locazione (è stata selezionata la voce °Sede presso Altrove"
        messages.error(request, "Imposta una locazione per procedere la navigazione del Corso.")

        # Rindirizzo utente sulla pagina di impostazione della locazione
        return redirect(reverse('aspirante:position_change', args=[corso.pk]))

    # Elaborazione del aggiornamento del documenti personali caricati
    if puoi_partecipare == CorsoBase.NON_HAI_CARICATO_DOCUMENTI_PERSONALI:
        if request.method == 'POST':
            doc = Documento(persona=me)
            load_personal_document_form = ModuloCreazioneDocumento(request.POST,
                request.FILES, instance=doc)

            if load_personal_document_form.is_valid():
                load_personal_document_form.save()
                return redirect(reverse('aspirante:info', kwargs={'pk': corso.pk}))
        else:
            load_personal_document_form = ModuloCreazioneDocumento()

        context['load_personal_document'] = load_personal_document_form

    context['corso'] = corso
    context['lezioni'] = corso.lezioni.all().order_by('inizio', 'fine', 'scheda_lezione_num',)
    context['puo_modificare'] = corso.can_modify(me)
    context['can_activate'] = corso.can_activate(me)
    context['puoi_partecipare'] = puoi_partecipare

    if corso.online:
        api = TrainingApi()
        r = api.core_course_get_courses_by_field_shortname(corso.titolo_cri.sigla)
        context['link'] = 'https://training.cri.it/course/view.php?id={}'.format(r['id'])


    return 'aspirante_corso_base_scheda_informazioni.html', context


@pagina_privata
def aspirante_corso_base_iscriviti(request, me=None, pk=None):
    corso = get_object_or_404(CorsoBase, pk=pk)

    puoi_partecipare = corso.persona(me)
    if not puoi_partecipare in corso.PUOI_ISCRIVERTI:
        return errore_generico(request, me,
           titolo="Non puoi partecipare a questo corso",
           messaggio="Siamo spiacenti, ma non sembra che tu possa partecipare "
                     "a questo corso per qualche motivo.",
           torna_titolo="Torna al corso",
           torna_url=corso.url)

    if corso.is_reached_max_participants_limit:
        corso.avvisa_presidente_raggiunto_limite_partecipazioni()

        return errore_generico(request, me,
           titolo="Non puoi partecipare a questo corso",
           messaggio="È stato raggiunto il limite massimo di richieste di "
                     "partecipazione al corso.",
           torna_titolo="Torna al corso",
           torna_url=corso.url)

    p = PartecipazioneCorsoBase(persona=me, corso=corso)
    p.save()
    p.richiedi()

    return messaggio_generico(request, me,
        titolo="Sei iscritt%s al corso" % me.genere_o_a,
        messaggio="Complimenti! La tua richiesta di iscrizione è stata registrata ed inviata al Direttore di Corso. "
                  "Nei prossimi giorni riceverai una e-mail di conferma o di respingimento della tua iscrizione.",
        torna_titolo="Torna al corso",
        torna_url=corso.url)


@pagina_privata
def aspirante_corso_base_ritirati(request, me=None, pk=None):
    corso = get_object_or_404(CorsoBase, pk=pk)
    partecipazione = PartecipazioneCorsoBase.objects.none()

    kwargs = dict(corso=corso, persona=me)
    if corso.persona(me) == CorsoBase.SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI:
        partecipazione = PartecipazioneCorsoBase.con_esito_ok(**kwargs).last()
    else:
        partecipazione = PartecipazioneCorsoBase.con_esito_pending(**kwargs).first()

    if partecipazione:
        # Caso: vuole ritirasi quando la richiesta non è stata ancora confermata
        partecipazione.ritira()

        # Caso: vuole ritirasi quando la richiesta è stata confermata
        if partecipazione.confermata:
            partecipazione.confermata = False
            partecipazione.save()  # second save() call

        # Informa direttore corso
        posta = Messaggio.costruisci_e_accoda(
            oggetto="Ritiro richiesta di iscrizione a %s da %s" % (corso.nome, partecipazione.persona),
            modello="email_corso_utente_ritirato_iscrizione.html",
            corpo={
                'corso': corso,
                'partecipante': partecipazione.persona,
            },
            destinatari=corso.direttori_corso())

        if posta:
            messages.success(request, "Il direttore del corso è stato avvisato.")

        return messaggio_generico(request, me,
            titolo="Ti sei ritirato dal corso",
            messaggio="La tua partecipazione al corso è stata annullata. "
                      "Ti ricordiamo che fino alla data di scadenza delle iscrizioni puoi iscriverti nuovamente a questo corso.",
            torna_titolo="Vai alla pagina dei corsi",
            torna_url=reverse('aspirante:corsi_base'))

    return messaggio_generico(request, me, titolo="Non puoi ritirarti da questo corso",
        messaggio="Siamo spiacenti, ma non sembra che tu possa ritirarti da questo corso per qualche motivo. ",
        torna_titolo="Torna alla pagina del corso",
        torna_url=corso.url)


@pagina_privata
@can_access_to_course
def aspirante_corso_base_mappa(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    puo_modificare = me.permessi_almeno(corso, MODIFICA)
    context = {
        "corso": corso,
        "puo_modificare": puo_modificare
    }
    return 'aspirante_corso_base_scheda_mappa.html', context


@pagina_privata
def aspirante_corso_base_lezioni(request, me, pk):
    gestione_lezioni = GestioneLezioni(request, me, pk)

    if not gestione_lezioni.ho_permesso:
        return redirect(ERRORE_PERMESSI)

    gestione_lezioni.presenze_assenze()

    return gestione_lezioni.get_http_response()


@pagina_privata
def course_lezione_save(request, me, pk, lezione_pk):
    gestione_lezioni = GestioneLezioni(request, me, pk, lezione_pk)

    if not gestione_lezioni.ho_permesso:
        return redirect(ERRORE_PERMESSI)

    saved = gestione_lezioni.save()
    if saved:
        return saved  # redirect to pagina lezioni

    return gestione_lezioni.get_http_response()


@pagina_privata
def aspirante_corso_base_lezioni_cancella(request, me, pk, lezione_pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    lezione = get_object_or_404(LezioneCorsoBase, pk=lezione_pk)
    if lezione.corso != corso:
        return redirect(ERRORE_PERMESSI)
    elif lezione.precaricata and not lezione.divisa:
        messages.error(request, "Non si può cancellare lezione pre-precaricata.")
        return redirect(corso.url_lezioni)

    deleted = lezione.delete()

    if deleted[0] > 0:
        pass


        # # Avvisa tutti i partecipanti che la lezione è stata rimossa
        # partecipanti = Persona.objects.filter(partecipazioni_corsi__in=corso.partecipazioni_confermate())
        #
        # sent_with_success = Messaggio.costruisci_e_accoda(
        #     oggetto="La lezione %s del %s è stata cancellata" % (lezione.nome,
        #                                                          corso.nome),
        #     modello="email_corso_lezione_cancella_avviso_partecipante.html",
        #     corpo={
        #         'corso': corso,
        #     },
        #     destinatari=partecipanti,
        # )
        #
        # if sent_with_success:
        #     msg = "La lezione è stata cancellata. Sono stati avvisati %s partecipanti del corso." % partecipanti.count()
        #     messages.success(request, msg)

    return redirect(corso.url_lezioni)


@pagina_privata
def aspirante_corso_base_modifica(request, me, pk):
    from .models import CorsoFile, CorsoLink
    from .forms import FormModificaCorsoSede
    from .formsets import CorsoFileFormSet, CorsoLinkFormSet

    course = get_object_or_404(CorsoBase, pk=pk)
    course_files = CorsoFile.objects.filter(corso=course)
    course_links = CorsoLink.objects.filter(corso=course)

    FILEFORM_PREFIX = 'files'
    LINKFORM_PREFIX = 'links'

    context = dict()

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

        if course_form.is_valid() and file_formset.is_valid() and link_formset.is_valid():

            if course_form.has_changed():
                messages.success(request, 'I dati della pianificazione corso sono stati salvati. '
                                          'Procedi con il prossimo step')
                return redirect(reverse('aspirante:lessons', args=[pk]))

            return redirect(reverse('aspirante:modify', args=[pk]))
    else:
        course_form = ModuloModificaCorsoBase(instance=course)
        file_formset = CorsoFileFormSet(queryset=course_files, prefix=FILEFORM_PREFIX)
        link_formset = CorsoLinkFormSet(queryset=course_links, prefix=LINKFORM_PREFIX)

        # Aggiungi form modifica sede se utente ha una delega per la sede del corso
        if me.deleghe_attuali(tipo__in=[RESPONSABILE_FORMAZIONE, PRESIDENTE],
                              oggetto_id=course.sede.comitato.id):
            context['sede_modifica_form'] = FormModificaCorsoSede(instance=course)

    context.update({
        'corso': course,
        'puo_modificare': True,
        'modulo': course_form,
        'file_formset': file_formset,
        'link_formset': link_formset,
    })
    return 'aspirante_corso_base_scheda_modifica.html', context


@pagina_privata
def aspirante_corso_base_attiva(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)

    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if corso.stato != corso.PREPARAZIONE:
        return messaggio_generico(request, me,
                                  titolo="Il corso è già attivo",
                                  messaggio="Non puoi attivare un corso già attivo",
                                  torna_titolo="Torna al Corso",
                                  torna_url=corso.url)
    if not corso.attivabile():
        return errore_generico(request, me,
                               titolo="Impossibile attivare questo corso",
                               messaggio="Non sono soddisfatti tutti i criteri di attivazione. "
                                         "Torna alla pagina del corso e verifica che tutti i "
                                         "criteri siano stati soddisfatti prima di attivare un "
                                         "nuovo corso.",
                               torna_titolo="Torna al Corso",
                               torna_url=corso.url)

    if corso.data_inizio < poco_fa():
        return errore_generico(request, me,
            titolo="Impossibile attivare un corso già iniziato",
            messaggio="Siamo spiacenti, ma non possiamo attivare il corso e inviare "
                "le e-mail a tutti gli interessati nella zona se il corso è già iniziato. "
                "Ti inviato a verificare i dati del corso.",
            torna_titolo="Torna al Corso",
            torna_url=corso.url
        )

    email_body = {"corso": corso, "persona": me}
    text = get_template("email_aspirante_corso_inc_testo.html").render(
        email_body)

    if request.POST:
        activation = corso.attiva(request=request, rispondi_a=me)

        volontari_da_informare = corso._corso_activation_recipients_for_email().count()

        if corso.extension_type == CorsoBase.EXT_MIA_SEDE:
            messages.success(request, "Saranno avvisati %s volontari del %s" % (volontari_da_informare, corso.sede))
        else:
            messages.success(request, "Saranno avvisati %s volontari dei comitati secondo le impostazioni delle estensioni." % volontari_da_informare)

        return activation

    context = {
        "corso": corso,
        "puo_modificare": True,
        "testo": text,
    }
    return 'aspirante_corso_base_scheda_attiva.html', context


@pagina_privata
def aspirante_corso_base_termina(request, me, pk):
    seconda_data_esame = '?seconda_data_esame' if 'seconda_data_esame' in request.GET else ""
    reverse_termina = reverse('aspirante:terminate', args=[pk])
    redirect_termina = redirect(reverse_termina + seconda_data_esame)

    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not corso.terminabile:
        messages.warning(request, "Il corso non è terminabile.")
        return redirect(reverse('aspirante:info', args=[pk]))

    if seconda_data_esame and not corso.data_esame_2:
        messages.error(request, "Impossibile generare il secondo verbale perchè non è impostata la seconda data di esame.")
        return redirect(corso.url)

    torna = {"torna_url": corso.url_modifica, "torna_titolo": "Modifica corso"}

    if not corso.partecipazioni_confermate().exists():
        return errore_generico(request, me, titolo="Impossibile terminare questo corso",
                               messaggio="Non ci sono partecipanti confermati per questo corso, "
                                         "non è quindi possibile generare un verbale per il corso.",
                               **torna)

    if corso.stato != corso.ATTIVO:
        return errore_generico(request, me, titolo="Impossibile terminare questo corso",
                               messaggio="Il corso non è attivo e non può essere terminato.",
                               **torna)

    partecipanti_moduli = list()

    azione = request.POST.get('azione', default=FormVerbaleCorso.SALVA_SOLAMENTE)
    generazione_verbale = azione == FormVerbaleCorso.GENERA_VERBALE
    termina_corso = generazione_verbale

    # Mostra partecipanti con motivo assente se l'azione è salvataggio form
    if seconda_data_esame:
        partecipanti_qs = corso.partecipazioni_confermate_assente_motivo(solo=True)
        data_ottenimento = corso.data_esame_2
    else:
        partecipanti_qs = corso.partecipazioni_confermate_assente_motivo()
        data_ottenimento = corso.data_esame

    if seconda_data_esame and not partecipanti_qs:
        # rindirizza sulla pagina del primo verbale se non ci sono
        # partecipanti da visualizzare nel secondo verbale
        return redirect(reverse_termina)

    # Variabili condizionali
    has_invalid_form = False

    # Validazione delle form
    for partecipante in partecipanti_qs:
        if corso.online:
            api = TrainingApi()
            form = FormVerbaleCorso(request.POST or None,
                prefix="part_%d" % partecipante.pk,
                instance=partecipante,
                generazione_verbale=generazione_verbale,
                initial={
                    'ammissione': PartecipazioneCorsoBase.AMMESSO
                    if api.ha_ottenuto_competenze(persona=partecipante.persona, corso=corso) else ''
                }
            )
        else:
            form = FormVerbaleCorso(
                request.POST or None,
                prefix="part_%d" % partecipante.pk,
                instance=partecipante,
                generazione_verbale=generazione_verbale
            )

        if corso.tipo == Corso.BASE:
            if corso.titolo_cri and corso.titolo_cri.scheda_prevede_esame:
                # GAIA-175 Campo destinazione prevede solo nel caso di esame
                # (come da scheda di valutazione personale
                form.fields['destinazione'].queryset = corso.possibili_destinazioni()
                form.fields['destinazione'].initial = corso.sede

        if form.is_valid():
            instance = form.save(commit=False)
            if instance.ammissione == PartecipazioneCorsoBase.ASSENTE_MOTIVO:
                # Serve per distinguere partecipanti per la generazione
                # dell'attestato e impostazione titolo cv.
                instance.esaminato_seconda_data = True
            else:
                # Se partecipante è stato segnato assente con motivazione nel
                # primo verbale, e poi per qualche ragione modificato con
                # ammesso/non ammesso bisogna togliere <esaminato_seconda_data>
                # se la data di oggi è maggiore di <data_esame> e minore di <data_esame_2>
                if instance.esaminato_seconda_data and (corso.data_esame_2 >
                                                        timezone.now() >=
                                                        corso.data_esame):
                    instance.esaminato_seconda_data = False
            instance.save()

        elif generazione_verbale:
            termina_corso = False
        else:
            has_invalid_form = True

        # Aggiungi la form nella lista che verra' inviata nel context
        partecipanti_moduli += [(partecipante, form)]

    if request.method == 'POST' and not has_invalid_form and not termina_corso:
        # Fai redirect (per aggiornare le form) solo ne caso non ci sono form
        # invalide (per visualizzare errori) e l'invio era per salvare (per
        # poter eseguire il codice sottostante)
        messages.success(request, 'Il verbale è stato salvato.')
        return redirect_termina

    if termina_corso:  # Se premuto pulsante "Genera verbale e termina corso"
        # Verifica se la relazione è compilata
        if not corso.relazione_direttore.is_completed:
            messages.error(request, "Il corso non può essere terminato perchè "
                                    "la relazione del direttore non è completata.")
            return redirect_termina

        # Verifica se nella form del verbale (sopra) sono stati salvati
        # partecipanti ammessi con motivo assente
        if seconda_data_esame and corso.has_partecipazioni_confermate_con_assente_motivo:
            messages.error(request, "Non puoi terminare il corso con le persone assenti. "
                                    "Imposta una seconda data e compila il secondo verbale")
            return redirect_termina

        if not corso.ha_compilato_commissione_esame:
            messages.error(request, "Impossibile terminare questo corso. Per generare il verbale è necessario "
                                    "che il presidente compili i dati della commissione esame ed inserisca la delibera.")
            Messaggio.costruisci_e_invia(
                oggetto='Inserimento commissione di esame del corso %s' %corso.nome,
                modello='email_corso_avvisa_presidente_da_compilare_commissione_esame.html',
                corpo={'corso': corso},
                destinatari=[corso.sede.presidente()]
            )

            if me == corso.get_firmatario:
                return redirect(corso.url_commissione_esame)
            return redirect_termina

        terminabile = corso.stato == corso.ATTIVO and corso.concluso and corso.partecipazioni_confermate().exists()
        if not terminabile:
            messages.warning(request, "Il corso non è terminabile perchè non è giunta la data di esame.")
            return redirect(reverse('aspirante:info', args=[pk]))

        # Tutto ok, posso procedere
        corso.termina(mittente=me,
                      partecipanti_qs=partecipanti_qs,
                      data_ottenimento=data_ottenimento)

        if corso.online:
            api = TrainingApi()
            api.cancellazione_iscritto(persona=partecipante.persona, corso=corso)

        if corso.is_nuovo_corso:
            torna_titolo = "Vai al Report del Corso"
            messaggio = "Tutti gli idonei hanno acquisito la qualifica prevista rispetto al corso frequentato."
        else:
            torna_titolo = "Vai al Report del Corso Base"
            messaggio = "Tutti gli idonei sono stati resi volontari delle rispettive sedi."

        return messaggio_generico(request, me,
          titolo="Generazione verbale",
          messaggio="Il verbale è stato generato con successo. %s" % messaggio,
          torna_titolo=torna_titolo,
          torna_url=corso.url_report)

    context = {
        "corso": corso,
        "puo_modificare": True,
        "partecipanti_moduli": partecipanti_moduli,
        "azione_genera_verbale": FormVerbaleCorso.GENERA_VERBALE,
        "azione_salva_solamente": FormVerbaleCorso.SALVA_SOLAMENTE,
    }
    return 'aspirante_corso_base_scheda_termina.html', context


@pagina_privata
def corso_compila_relazione_direttore(request, me, pk):
    course = get_object_or_404(CorsoBase, pk=pk)
    puo_modificare = course.can_modify(me)
    if not puo_modificare:
        return redirect(ERRORE_PERMESSI)

    if not course.terminabile:
        messages.warning(request, 'Il corso non è terminabile.')
        return redirect(reverse('aspirante:info', args=[pk,]))

    relazione, created = RelazioneCorso.objects.get_or_create(corso=course)
    if request.method == 'POST':
        form_relazione = FormRelazioneDelDirettoreCorso(request.POST, instance=relazione)
        if form_relazione.is_valid():
            cd = form_relazione.cleaned_data
            instance = form_relazione.save(commit=False)

            # Se nei vari il Direttore non ha nulla da inserire valorizzarlo con un valore di default
            no_value_fields = [k for k,v in cd.items() if not v]
            if no_value_fields:
                for k in no_value_fields:
                    setattr(instance, k, RelazioneCorso.SENZA_VALORE)
            instance.save()

            messages.success(request, 'La relazione è stata salvata.')
            return redirect(reverse('courses:compila_relazione_direttore', args=(pk,)))
    else:
        form_relazione = FormRelazioneDelDirettoreCorso(instance=relazione)

    context = {
        "corso": course,
        "puo_modificare": puo_modificare,
        "form_relazione": form_relazione,
    }
    return 'course_compila_relazione_direttore.html', context


@pagina_privata
def aspirante_corso_base_iscritti(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)

    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    elenco = ElencoPartecipantiCorsiBase(corso.queryset_modello())
    in_attesa = corso.partecipazioni_in_attesa()
    context = {
        "corso": corso,
        "puo_modificare": True,
        "elenco": elenco,
        "in_attesa": in_attesa,
    }
    return 'aspirante_corso_base_scheda_iscritti.html', context


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
        return errore_generico(request, me,
           titolo="Impossibile aggiungere iscritti",
           messaggio="Non si possono aggiungere altri iscritti a questo "
                     "stadio della vita del corso.",
           torna_titolo="Torna al corso",
           torna_url=corso.url_iscritti
        )

    risultati = list()
    persone_con_esito_negativo = dict()

    form = ModuloIscrittiCorsoBaseAggiungi(request.POST or None, corso=corso)
    if form.is_valid():
        for persona in form.cleaned_data['persone']:
            # esito_negative_message = None
            esito = corso.persona(persona)
            if esito in [CorsoBase.NON_HAI_CARICATO_DOCUMENTI_PERSONALI, CorsoBase.NON_HAI_DOCUMENTO_PERSONALE_VALIDO]:
                persone_con_esito_negativo[persona] = esito

            #     esito_negative_message = "Questo utente non ha caricato un documento d'identità"
            # elif esito == CorsoBase.NON_HAI_DOCUMENTO_PERSONALE_VALIDO:
            #     esito_negative_message = "Questo utente non ha un documento di riconoscimento valido/rinnovato"

            # # Persone da avvisare via posta della problematica
            # if esito_negative_message:
            #     persone_con_esito_negativo[persona] = esito #, esito_negative_message

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
                    partecipazione = PartecipazioneCorsoBase.objects.create(
                        persona=persona,
                        corso=corso
                    )
                    ok = PartecipazioneCorsoBase.ISCRITTO

                    if corso.is_nuovo_corso:
                        subject = "Iscrizione a %s" % corso.titolo_cri
                    else:
                        subject = "Iscrizione a Corso Base"

                    Messaggio.costruisci_e_invia(
                        oggetto=subject,
                        modello="email_corso_invito_con_conferma.html",
                        corpo={
                            "persona": persona,
                            "corso": corso,
                        },
                        mittente=me,
                        destinatari=[persona]
                    )

                if corso.online:
                    from formazione.training_api import TrainingApi
                    api = TrainingApi()
                    api.aggiugi_ruolo(persona=persona, corso=corso, ruolo=TrainingApi.DISCENTE)

                Log.crea(me, partecipazione)

            risultati += [{
                "persona": persona,
                "partecipazione": partecipazione,
                "esito": esito,
                "ok": ok,
            }]

        # Invia avvisi agli utenti con esito negativo
        for persona, esito in persone_con_esito_negativo.items():
            already_sent_today = Messaggio.objects.filter(
                mittente=me,
                oggetti_destinatario__persona=persona,
                oggetto__istartswith="Impossibilità di iscriversi a",
                creazione__date=date.today(),
            ).count()

            # Per evitare che invii lo stesso messaggio più di una volta al di
            if not already_sent_today:
                posta = Messaggio.costruisci_e_accoda(
                    oggetto="Impossibilità di iscriversi a %s" % corso.nome,
                    modello="email_corso_iscritti_aggiungi_esito_negativo.html",
                    corpo={
                        'corso': corso,
                        'esito': esito,
                    },
                    mittente=me,
                    destinatari=[persona])
        else:
            if persone_con_esito_negativo:
                utente = 'utenti' if len(persone_con_esito_negativo) > 1 else 'utente'
                messages.error(request, "Abbiamo avvisato %s della problematica." % utente)

    context = {
        "corso": corso,
        "puo_modificare": True,
        "modulo": form,
        "risultati": risultati,
    }
    return 'aspirante_corso_base_scheda_iscritti_aggiungi.html', context


@pagina_privata
def aspirante_corso_base_firme(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    archivio = corso.genera_pdf_firme(request=request)
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

    can_download = False
    if request.GET.get('download_single_attestato') and corso.partecipazioni_confermate().get(persona=me):
        can_download = True

    if not can_download and not me.permessi_almeno(corso, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    report = GeneraReport(request, corso)
    return report.download()


@pagina_privata
def aspirante_home(request, me):
    if not me.ha_aspirante:
        return redirect(ERRORE_PERMESSI)

    contesto = {}
    return 'aspirante_home.html', contesto


@pagina_privata
@can_access_to_course
def aspirante_corsi(request, me):
    """ url: /aspirante/corsi/ """

    corsi = CorsoBase.objects.none()

    if me.ha_aspirante:
        corsi = me.aspirante.corsi().exclude(tipo=Corso.CORSO_NUOVO)
    elif me.volontario or me.dipendente:
        mie_sedi = me.sedi_appartenenze_corsi

        # Trova corsi dove l'utente ha già partecipato
        partecipazione = PartecipazioneCorsoBase.objects.filter(confermata=True, persona=me)
        corsi_confermati = CorsoBase.objects.filter(
            stato__in=[CorsoBase.ATTIVO, CorsoBase.TERMINATO],
            id__in=partecipazione.values_list('corso', flat=True))

        # Trova corsi con estensione sede di mia appartenenze
        corsi_estensione_mia_appartenenze = CorsoBase.objects.filter(
            tipo__isnull=False,
            stato=CorsoBase.ATTIVO,
            extension_type=CorsoBase.EXT_MIA_SEDE,
            sede__in=mie_sedi,
            titolo_cri__isnull=False,)

        # Trova corsi da partecipare
        corsi_da_partecipare = CorsoBase.find_courses_for_volunteer(volunteer=me, sede=mie_sedi)

        # Unisci 2 categorie di corsi
        corsi = corsi_confermati | corsi_da_partecipare | corsi_estensione_mia_appartenenze
        corsi = corsi.filter(tipo__in=[Corso.CORSO_NUOVO, Corso.CORSO_ONLINE])

    corsi_frequentati = me.corsi_frequentati
    corsi_attivi = corsi.exclude(pk__in=corsi_frequentati.values_list('pk', flat=True))

    context = {
        'corsi_attivi': corsi_attivi.order_by('data_inizio',),
        'corsi_frequentati': corsi_frequentati,
        'puo_creare': True if me.ha_permesso(GESTIONE_CORSI_SEDE) else False
    }
    return 'aspirante_corsi.html', context


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
    from .forms import CorsoSelectExtensionTypeForm
    from .formsets import CorsoSelectExtensionFormSet

    SELECT_EXTENSION_TYPE_FORM_PREFIX = 'extension_type'
    SELECT_EXTENSIONS_FORMSET_PREFIX = 'extensions'

    course = get_object_or_404(CorsoBase, pk=pk)

    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not course.tipo == Corso.CORSO_NUOVO and not course.tipo == Corso.CORSO_ONLINE:
        # The page is not accessible if the type of course is not CORSO_NUOVO or CORSO_ONLINE
        return redirect(ERRORE_PERMESSI)

    if request.method == 'POST':
        select_extension_type_form = CorsoSelectExtensionTypeForm(request.POST,
                                    instance=course,
                                    prefix=SELECT_EXTENSION_TYPE_FORM_PREFIX)
        select_extensions_formset = CorsoSelectExtensionFormSet(request.POST,
                                    prefix=SELECT_EXTENSIONS_FORMSET_PREFIX,
                                    form_kwargs={'corso': course})

        if select_extension_type_form.is_valid() and select_extensions_formset.is_valid():
            select_extensions_formset.save(commit=False)

            for form in select_extensions_formset:
                if form.is_valid:
                    cd = form.cleaned_data
                    instance = form.save(commit=False)
                    instance.corso = course
                    corso = instance.corso

                    # Skip blank extra formset
                    if cd == {} and len(select_extensions_formset) > 1:
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

                # Set EXT_MIA_SEDE if course has no extensions
                reset_corso_ext = CorsoBase.objects.get(pk=pk)
                corso_has_extensions = reset_corso_ext.has_extensions()
                new_objects = select_extensions_formset.new_objects
                if not corso_has_extensions and not new_objects:
                    reset_corso_ext.extension_type = CorsoBase.EXT_MIA_SEDE
                    reset_corso_ext.save()

                # Reindirizzare l'utente al prossimo step da compilare (utile
                # solo in fase di primo compilamento delle form del corso).
                if corso_has_extensions or new_objects:
                    messages.success(request, 'Le estensioni sono state salvate. Procedi con il prossimo step')
                    return redirect(reverse('aspirante:modify', args=[pk]))

                return redirect(reverse('aspirante:estensioni_modifica', args=[pk]))

    else:
        select_extension_type_form = CorsoSelectExtensionTypeForm(
            prefix=SELECT_EXTENSION_TYPE_FORM_PREFIX,
            instance=course,
        )
        select_extensions_formset = CorsoSelectExtensionFormSet(
            prefix=SELECT_EXTENSIONS_FORMSET_PREFIX,
            form_kwargs={'corso': course},
            queryset=CorsoEstensione.objects.filter(corso=course)
        )

    context = {
        'corso': course,
        'puo_modificare': True,
        'select_extension_type_form': select_extension_type_form,
        'select_extensions_formset': select_extensions_formset,
    }
    return 'aspirante_corso_estensioni_modifica.html', context


@pagina_privata
def aspirante_corso_estensioni_informa(request, me, pk):
    from .forms import InformCourseParticipantsForm

    course = get_object_or_404(CorsoBase, pk=pk)

    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    qs = Persona.objects.filter()
    form_data = {
        'instance': course,
    }
    form = InformCourseParticipantsForm(request.POST or None, **form_data)
    if form.is_valid():
        cd = form.cleaned_data
        recipients = PartecipazioneCorsoBase.objects.none()
        sent_with_success = False

        recipient_type = cd['recipient_type']
        if recipient_type == form.ALL:
            recipients = course.partecipazioni_in_attesa() | course.partecipazioni_confermate()
        elif recipient_type == form.UNCONFIRMED_REQUESTS:
            recipients = course.partecipazioni_in_attesa()
        elif recipient_type == form.CONFIRMED_REQUESTS:
            recipients = course.partecipazioni_confermate()
        elif recipient_type == form.INVIA_QUESTIONARIO:
            # recipients = course.partecipazioni_confermate()
            return redirect(reverse('courses:send_questionnaire_to_participants', args=[course.pk]))
        else:
            # todo: something went wrong ...
            pass

        if recipients and not recipient_type == form.INVIA_QUESTIONARIO:
            sent_with_success = Messaggio.costruisci_e_invia(
                oggetto="Informativa dal direttore %s (%s)" % (course.nome, course.titolo_cri),
                modello="email_corso_informa_participants.html",
                corpo={
                    'corso': course,
                    'message': cd['message'],
                },
                mittente=me,
                destinatari=[r.persona for r in recipients]
            )

        if sent_with_success:
            messages.success(request, "Il messaggio ai volontari è stato inviato con successo.")
            return redirect(reverse('aspirante:informa', args=[pk]))

        if not recipients:
            messages.success(request,  "Il messaggio non è stato inviato a nessuno.")
            return redirect(reverse('aspirante:informa', args=[pk]))

    context = {
        'corso': course,
        'form': form,
        'puo_modificare': True,
    }
    return 'aspirante_corso_informa_persone.html', context


@pagina_privata
def formazione_albo_informatizzato(request, me):
    sedi_set = set()

    ALL_PERMESSI_TO_CHECK = RUBRICA_DELEGATI_OBIETTIVO_ALL + [GESTIONE_CORSI_SEDE]
    for permesso in ALL_PERMESSI_TO_CHECK:
        ids = me.oggetti_permesso(permesso).values_list('pk', flat=True)
        sedi_set.update(ids)

    sedi = Sede.objects.filter(pk__in=sedi_set)

    if not sedi:
        return redirect(ERRORE_PERMESSI)

    context = {
        'elenco_nome': 'Albo Informatizzato',
        'elenco_template': None,
    }

    # Step 2: Elaborare elenco per le sedi selezionate
    if request.method == 'POST':
        elenco = ElencoPerTitoliCorso(sedi.filter(pk__in=request.POST.getlist('sedi')))
        context['elenco'] = elenco
        return 'formazione_albo_elenco_generico.html', context

    # Step 1: Selezione sedi
    context['sedi'] = sedi
    return 'formazione_albo_informatizzato.html', context


@pagina_privata
def formazione_albo_titoli_corso_full_list(request, me):
    context = {}
    if 'persona_id' in request.GET:
        persona = Persona.objects.get(id=request.GET['persona_id'])
        titles = TitoloPersonale.objects.filter(persona=persona,
                                                is_course_title=True)
        context['titles'] = titles.order_by('titolo__nome', '-data_scadenza')
        context['person'] = persona

    return 'formazione_albo_titoli_corso_full_list.html', context


@pagina_privata
def formazione_corso_position_change(request, me, pk):
    """
    La pagina renderizzata viene aggiornata con redirect sulla pagina direttore corso.
    Per non avere refresh aggiungere ?norefresh alla url a questa view.
    """
    course = get_object_or_404(CorsoBase, pk=pk)

    if request.POST and request.POST.get('modifica_sede_dopo_attivazione') and \
        request.POST.get('locazione') == ModuloCreazioneCorsoBase.PRESSO_SEDE:
        course.locazione = course.sede.locazione
        course.save()
        messages.success(request, 'La sede del corso è stata modificata.')
        return redirect(reverse('aspirante:modify', args=[pk]))

    if not course.can_modify(me):
        return redirect(ERRORE_PERMESSI)

    template = 'formazione_vuota.html'
    puo_modificare = False  # non mostrare i tab se la locazione non è impostata

    # Locazione impostata...
    if course.locazione:
        template = 'aspirante_corso_base_scheda.html'
        puo_modificare = course.can_modify(me)
        # Se il corso non ha ancora un direttore...
        if not course.direttori_corso:
            # Rindirizza sulla pagina selezione direttori del corso.
            return redirect(course.url_direttori)

    context = {'corso': course,
               'template': template,
               'puo_modificare': puo_modificare,}

    return 'formazione_corso_position_change.html', context


@pagina_privata
def course_send_questionnaire_to_participants(request, me, pk):
    context = dict()
    course = get_object_or_404(CorsoBase, pk=pk)

    if not course.can_modify(me):
        return redirect(ERRORE_PERMESSI)

    if request.method == 'POST':
        send_with_success = False

        recipients = request.POST.getlist('persona')
        recipients = Persona.objects.filter(id__in=[int(r) for r in recipients])
        if recipients:
            titolo = 'per %s' % course.titolo_cri if course.titolo_cri else ''
            sent_with_success = Messaggio.costruisci_e_invia(
                oggetto="Questionario di gradimento del %s %s" % (course.nome, titolo),
                modello="email_corso_questionario_gradimento.html",
                corpo={
                    'corso': course,
                },
                mittente=me,
                destinatari=recipients,
            )

            if sent_with_success:
                msg = "Il questionario è stato inviato con successo a %s partecipanti selezionati" % recipients.count()
                messages.success(request, msg)
                return redirect(reverse('courses:send_questionnaire_to_participants', args=[course.pk]))
        else:
            messages.error(request, 'Non hai selezionato persone.')

    context['puo_modificare'] = course.can_modify(me)
    context['corso'] = course

    return 'course_send_questionnaire_to_participants.html', context


@pagina_privata
def course_materiale_didattico_download(request, me, pk):
    from .models import CorsoFile

    corso = get_object_or_404(CorsoBase, pk=pk)
    partecipante = corso.persona(me) if me else None

    if partecipante in CorsoBase.SEI_ISCRITTO or me.permessi_almeno(corso, MODIFICA):
        try:
            # Identificatore nella richiesta
            file_id = request.GET.get('id')
            if not file_id:
                raise Http404

            # File esiste
            materiale = CorsoFile.objects.get(pk=int(file_id))  # fallisce se si passa non un number
            file_path = materiale.file.path

            if not materiale.file.storage.exists(materiale.file):
                return HttpResponse('Il file non si trova.')

            # Preparare la risposta
            with open(file_path, 'rb') as f:
                response = HttpResponse(content=f.read(),
                                        content_type='application/force-download')
            filename = '_'.join(materiale.filename().split())
            response['Content-Disposition'] = 'attachment; filename=%s' % filename

            # Incrementare il contatore
            materiale.download_count = F('download_count') + 1
            materiale.save()

            return response
        except:
            pass

    return HttpResponse('Non hai accesso a questo file.')


@pagina_privata
def course_commissione_esame(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)

    # if me in corso.direttori_corso() and me == corso.sede.presidente():
    #     messages.error(request, "Non c'è possibilità di inserire la commissione di esame e "
    #                             "non si può procedere alla chiusura del corso "
    #                             "se il presidente e il direttore del corso sono la stessa persona")
    #     return redirect(corso.url)

    if request.method == 'POST':
        form = FormCommissioneEsame(request.POST, request.FILES, instance=corso)
        if form.is_valid():
            cd = form.cleaned_data
            nominativi = [v for k,v in cd.items() if k.startswith('nominativo_') and v]
            esame_names = ', '.join(sorted(nominativi))

            instance = form.save(commit=False)
            instance.commissione_esame_names = esame_names
            instance.save()

            # Avvisa il presidente del comitato del corso
            nuovo_avviso = False

            oggetto = 'Inserimento della commissione di esame del corso %s' % corso.nome
            modello = 'email_corso_avvisa_presidente_inserimento_commissione_esame.html'
            corpo = {'corso': corso}

            # Verifica se stesso messaggio non è stato ancora inviato
            avvisi = Messaggio.objects.filter(oggetto=oggetto)
            if not avvisi:
                nuovo_avviso = True
            else:
                email_body = get_template(modello).render(corpo)
                ultimo_avviso_corpo = avvisi.last().corpo
                ultimo_avviso_corpo = ultimo_avviso_corpo[ultimo_avviso_corpo.find('|||') + 3:ultimo_avviso_corpo.find('===')]

                if len(ultimo_avviso_corpo) != len(esame_names):
                    nuovo_avviso = True

            if nuovo_avviso and me != corso.sede.presidente():
                Messaggio.costruisci_e_invia(
                    oggetto=oggetto,
                    modello=modello,
                    corpo=corpo,
                    destinatari=[corso.sede.presidente()]
                )
                messages.success(request, 'La commissione di esame è stata inserita correttamente.')
                messages.success(request, 'Il presidente del comitato è stato avvisato del inserimento della commissione esame.')

            return redirect(reverse('courses:commissione_esame', args=[pk]))
    else:
        form = FormCommissioneEsame(instance=corso)

    context = {
        'corso': corso,
        'commissione_esame_form': form,
    }
    return 'course_commissione_esame.html', context


@pagina_privata
def catalogo_corsi(request, me):
    from curriculum.areas import OBBIETTIVI_STRATEGICI
    from .forms import CatalogoCorsiSearchForm

    context = {
        'titoli': OrderedDict(),
        'titoli_online': OrderedDict(),
        'form': CatalogoCorsiSearchForm,
    }

    search_query = 'q' in request.GET and request.GET.get('q')
    if search_query:
        qs = Titolo.objects.filter(
            Q(Q(sigla__icontains=search_query) | Q(nome__icontains=search_query)),
            tipo=Titolo.TITOLO_CRI, sigla__isnull=False)
    else:
        qs = Titolo.objects.filter(tipo=Titolo.TITOLO_CRI, sigla__isnull=False)

    context = costruisci_titoli(context, qs.filter(online=False), search_query, 'titoli')
    context = costruisci_titoli(context, qs.filter(online=True), search_query, 'titoli_online')

    context['titoli_total'] = qs.count()

    return 'catalogo_corsi.html', context
