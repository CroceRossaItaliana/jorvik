import json
from datetime import date, timedelta, datetime, time

from django.db.models import Count, F, Sum
from django.utils import timezone
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, get_object_or_404

from anagrafica.costanti import NAZIONALE
from anagrafica.models import Sede
from anagrafica.forms import ModuloProfiloModificaAnagraficaDatoreLavoro
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA, DELEGATO_AREA, REFERENTE, REFERENTE_GRUPPO
from anagrafica.permessi.costanti import MODIFICA, GESTIONE_ATTIVITA, ERRORE_PERMESSI, GESTIONE_GRUPPO, \
    GESTIONE_AREE_SEDE, COMPLETO, GESTIONE_ATTIVITA_AREA, GESTIONE_REFERENTI_ATTIVITA, GESTIONE_ATTIVITA_SEDE, \
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE, GESTIONE_SALA_OPERATIVA_SEDE
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import ci_siamo_quasi, errore_generico, messaggio_generico, errore_no_volontario
from base.utils import poco_fa, timedelta_ore
from gruppi.models import Gruppo
from .models import ReperibilitaSO, ServizioSO


# todo: da integrare in questa app
from attivita.stats import statistiche_attivita_persona
from attivita.elenchi import ElencoPartecipantiTurno, ElencoPartecipantiAttivita
from attivita.utils import turni_raggruppa_giorno
# todo:

from .models import PartecipazioneSO, ServizioSO, TurnoSO, AreaSO
from .forms import (StoricoTurniForm, AttivitaInformazioniForm, OrganizzaAttivitaForm,
    ModificaTurnoForm, AggiungiPartecipantiForm, CreazioneTurnoForm,
    RipetiTurnoForm, CreazioneAreaForm, StatisticheAttivitaForm,
    OrganizzaAttivitaReferenteForm, StatisticheAttivitaPersonaForm,
    VolontarioReperibilitaForm, AggiungiReperibilitaPerVolontarioForm, )


INITIAL_INIZIO_FINE_PARAMS = {
    "inizio": poco_fa() + timedelta(hours=1),
    "fine": poco_fa() + timedelta(hours=2),
}


def get_reverse(id, sede_pk=None, area_pk=None, attivita_pk=None):
    REVERSE_MAP = {
        1: reverse('so:aree_sede', args=[sede_pk,]),
        2: reverse('so:sede_area_responsabili', args=[sede_pk, area_pk,]),
        3: reverse('so:gestisci'),
        4: reverse('so:organizza_referenti_fatto', args=[attivita_pk,]),
    }
    return REVERSE_MAP[id]


@pagina_privata
def so_index(request, me):
    if not me.volontario:
        return redirect('/')

    sedi = me.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    if not sedi:
        return redirect(reverse('so:reperibilita'))

    context = {
        'ora': poco_fa(),
        'sedi': sedi,
        'reperibilita': ReperibilitaSO.reperibilita_per_sedi(sedi),
    }
    return 'sala_operativa_index.html', context


@pagina_privata
def so_reperibilita(request, me):
    if me.ha_datore_di_lavoro:
        form = VolontarioReperibilitaForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
    else:
        form = ModuloProfiloModificaAnagraficaDatoreLavoro(request.POST or None, instance=me)

    if request.method == 'POST':
        if form.is_valid():
            if me.ha_datore_di_lavoro:
                cd = form.cleaned_data
                reperibilita = form.save(commit=False)
                reperibilita.persona = me
                reperibilita.save()
                messages.success(request, "La nuova reperibilità è stata creata.")
            else:
                messages.error(request, "Non hai comunicato i dati del datore di lavoro nella tua anagrafica.")
                form.save()
            return redirect(reverse('so:reperibilita'))

    context = {
        'me': me,
        'form': form,
        'reperibilita': ReperibilitaSO.reperibilita_di(me)[:50],
    }
    return 'sala_operativa_reperibilita.html', context


@pagina_privata
def so_reperibilita_cancella(request, me, pk):
    if not me.volontario:
        return redirect('/')
    reperibilita = get_object_or_404(ReperibilitaSO, pk=pk)
    if me not in [reperibilita.persona, reperibilita.creato_da, ]:
        return redirect(ERRORE_PERMESSI)
    reperibilita.delete()
    messages.success(request, 'La reperibilita selezionata è stata rimossa.')
    return redirect(reverse('so:index'))


@pagina_privata
def so_reperibilita_edit(request, me, pk):
    if not me.volontario:
        return redirect('/')

    reperibilita = get_object_or_404(ReperibilitaSO, pk=pk)
    if reperibilita.creato_da != me:
        return redirect(ERRORE_PERMESSI)

    form = VolontarioReperibilitaForm(request.POST or None, instance=reperibilita)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('so:reperibilita_backup'))
    context = {
        'form': form,
        'reperibilita': reperibilita,
    }
    return 'sala_operativa_reperibilita_edit.html', context


@pagina_privata
def so_reperibilita_backup(request, me):
    form = AggiungiReperibilitaPerVolontarioForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            reperibilita = form.save(commit=False)
            reperibilita.persona = cd['persona']
            reperibilita.creato_da = me
            reperibilita.save()
            return redirect(reverse('so:reperibilita_backup'))

    context = {
        'form': form,
        'reperibilita': ReperibilitaSO.reperibilita_create_da(me),
    }
    return 'sala_operativa_reperibilita_per_volontario_aggiungi.html', context


@pagina_privata
def so_aree(request, me):
    sedi = me.oggetti_permesso(GESTIONE_AREE_SEDE)
    context = {
        "sedi": sedi,
    }
    return 'so_aree.html', context


@pagina_privata
def so_aree_sede(request, me, sede_pk=None):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not sede in me.oggetti_permesso(GESTIONE_AREE_SEDE):
        return redirect(ERRORE_PERMESSI)
    aree = sede.aree.all()
    form = CreazioneAreaForm(request.POST or None)
    if form.is_valid():
        area = form.save(commit=False)
        area.sede = sede
        area.save()
        return redirect(get_reverse(2, sede_pk=sede.pk, area_pk=area.pk))
    context = {
        "sede": sede,
        "aree": aree,
        "modulo": form,
    }
    return 'so_aree_sede.html', context


@pagina_privata
def so_aree_sede_area_responsabili(request, me, sede_pk=None, area_pk=None):
    area = get_object_or_404(AreaSO, pk=area_pk)

    if not me.permessi_almeno(area, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    delega = DELEGATO_AREA
    sede = area.sede

    context = {
        "area": area,
        "delega": delega,
        "continua_url": get_reverse(1, sede_pk=sede.pk),
    }
    return 'so_aree_sede_area_responsabili.html', context


@pagina_privata
def so_aree_sede_area_cancella(request, me, sede_pk=None, area_pk=None):
    area = get_object_or_404(AreaSO, pk=area_pk)
    if not me.permessi_almeno(area, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    sede = area.sede
    if area.attivita.exists():
        return errore_generico(request, me, titolo="L'area ha dei servizi associati",
                               messaggio="Non è possibile cancellare delle aree che hanno deservizi associati.",
                               torna_titolo="Torna indietro",
                               torna_url=get_reverse(1, sede_pk=sede.pk))
    area.delete()
    return redirect(get_reverse(1, sede_pk=sede.pk))


@pagina_privata
def so_gestisci(request, me, stato="aperte"):
    # todo: renaming in view, template

    # stato = "aperte" | "chiuse"

    attivita_tutte = me.oggetti_permesso(GESTIONE_ATTIVITA, solo_deleghe_attive=False)
    attivita_aperte = attivita_tutte.filter(apertura=ServizioSO.APERTA)
    attivita_chiuse = attivita_tutte.filter(apertura=ServizioSO.CHIUSA)

    if stato == "aperte":
        attivita = attivita_aperte
    else:  # stato == "chiuse"
        attivita = attivita_chiuse

    attivita_referenti_modificabili = me.oggetti_permesso(GESTIONE_REFERENTI_ATTIVITA)

    attivita = attivita.annotate(num_turni=Count('turni'))
    attivita = Paginator(attivita, 30)
    pagina = request.GET.get('pagina')

    try:
        attivita = attivita.page(pagina)
    except PageNotAnInteger:
        attivita = attivita.page(1)
    except EmptyPage:
        attivita = attivita.page(attivita.num_pages)

    context = {
        "stato": stato,
        "attivita": attivita,
        "attivita_aperte": attivita_aperte,
        "attivita_chiuse": attivita_chiuse,
        "attivita_referenti_modificabili": attivita_referenti_modificabili,
    }
    return 'so_gestisci.html', context


@pagina_privata
def so_organizza(request, me):
    from anagrafica.models import Persona

    aree = me.oggetti_permesso(GESTIONE_ATTIVITA_AREA)

    if not aree:
        return messaggio_generico(request, me, titolo="Crea un'area di intervento, prima!",
                                  messaggio="Le aree di intervento fungono da 'contenitori' per le "
                                            "attività. Per organizzare un'attività, è necessario creare "
                                            "almeno un'area di intervento. ",
                                  torna_titolo="Gestisci le Aree di intervento",
                                  torna_url=reverse('so:aree'))

    modulo_referente = OrganizzaAttivitaReferenteForm(request.POST or None)

    form = OrganizzaAttivitaForm(request.POST or None)
    form.fields['area'].queryset = me.oggetti_permesso(GESTIONE_ATTIVITA_AREA)

    if modulo_referente.is_valid() and form.is_valid():
        attivita = form.save(commit=False)
        attivita.sede = attivita.area.sede
        attivita.estensione = attivita.sede.comitato
        attivita.save()

        # Crea gruppo per questa specifica attività se la casella viene selezionata.
        crea_gruppo = form.cleaned_data['gruppo']
        if crea_gruppo:
            area = attivita.area
            gruppo = Gruppo.objects.create(nome=attivita.nome,
                                           sede=attivita.sede,
                                           obiettivo=area.obiettivo,
                                           attivita=attivita,
                                           estensione=attivita.estensione.estensione,
                                           area=area)

            gruppo.aggiungi_delegato(REFERENTE_GRUPPO, me)

        if modulo_referente.cleaned_data['scelta'] == modulo_referente.SONO_IO:
            # Io sono il referente.
            attivita.aggiungi_delegato(REFERENTE, me, firmatario=me, inizio=poco_fa())
            return redirect(attivita.url_modifica)
        elif modulo_referente.cleaned_data['scelta'] == modulo_referente.SCEGLI_REFERENTI:  # Il referente e' qualcun altro.
            return redirect(reverse('so:organizza_referenti', args=[attivita.pk,]))
        else:
            persona = Persona.objects.get(pk=modulo_referente.cleaned_data['scelta'])
            attivita.aggiungi_delegato(REFERENTE, persona, firmatario=me, inizio=poco_fa())
            return redirect(attivita.url_modifica)

    context = {
        "modulo": form,
        "modulo_referente": modulo_referente,
    }
    return 'so_organizza.html', context


@pagina_privata
def so_organizza_fatto(request, me, pk=None):
    attivita = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    return messaggio_generico(request, me, titolo="Attività organizzata",
                              messaggio="Abbiamo inviato un messaggio ai referenti che hai "
                                        "selezionato. Appena accederanno a Gaia, gli chiederemo "
                                        "di darci maggiori informazioni sull'attività, come "
                                        "gli orari dei turni e l'indirizzo.",
                              torna_titolo="Torna a Gestione Attività",
                              torna_url=reverse('so:gestisci'))


@pagina_privata
def so_referenti(request, me, pk=None, nuova=False):
    attivita = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    delega = REFERENTE

    if nuova:
        continua_url = get_reverse(4, attivita_pk=attivita.pk)
    else:
        continua_url = get_reverse(3)

    context = {
        "delega": delega,
        "attivita": attivita,
        "continua_url": continua_url
    }
    return 'so_referenti.html', context


@pagina_privata
def so_calendario(request, me=None, inizio=None, fine=None, vista="calendario"):
    # todo: urls reverse

    """Mostra il calendario delle attivita' personalizzato."""
    if not me.volontario:
        return errore_no_volontario(request, me)

    # Range default e massimo
    DEFAULT_GIORNI = 6
    MASSIMO_GIORNI = 31

    # Formato date URL
    FORMATO = "%d-%m-%Y"

    if inizio is None:
        inizio = date.today().strftime(FORMATO)

    inizio = datetime.strptime(inizio, FORMATO).date()

    if fine is None:
        fine = inizio + timedelta(DEFAULT_GIORNI)
    else:
        fine = datetime.strptime(fine, FORMATO).date()

    # Assicura che il range sia valido (non troppo breve, non troppo lungo)
    differenza = (fine - inizio)
    if differenza.days < 0 or differenza.days > MASSIMO_GIORNI:
        return so_calendario(request, me, inizio=inizio, fine=None)

    # Successivo
    successivo_inizio = inizio + differenza
    successivo_inizio_stringa = successivo_inizio.strftime(FORMATO)
    successivo_fine = fine + differenza
    successivo_fine_stringa = successivo_fine.strftime(FORMATO)

    successivo_url = reverse('so:calendario_con_range', args=[successivo_inizio_stringa,
                                                              successivo_fine_stringa,])

    # Oggi
    oggi_url = reverse('so:calendario')

    # Precedente
    precedente_inizio = inizio - differenza
    precedente_inizio_stringa = precedente_inizio.strftime(FORMATO)
    precedente_fine = fine - differenza
    precedente_fine_stringa = precedente_fine.strftime(FORMATO)

    precedente_url = reverse('so:calendario_con_range', args=[precedente_inizio_stringa,
                                                              precedente_fine_stringa,])

    # Elenco
    turni = me.calendario_turni(inizio, fine)
    raggruppati = turni_raggruppa_giorno(turni)

    context = {
        "inizio": inizio,
        "fine": fine,

        "successivo_inizio": successivo_inizio,
        "successivo_fine": successivo_fine,
        "successivo_url": successivo_url,

        "oggi_url": oggi_url,

        "precedente_inizio": precedente_inizio,
        "precedente_fine": precedente_fine,
        "precedente_url": precedente_url,

        "turni": turni,
        "raggruppati": raggruppati,
    }

    return 'so_calendario.html', context


@pagina_privata
def so_storico(request, me):
    """Mostra uno storico dei servizi a cui ho chiesto di partecipare/partecipato"""

    storico = PartecipazioneSO.objects.filter(persona=me).order_by('-turno__inizio')
    form = StatisticheAttivitaPersonaForm(request.POST or None)
    statistiche = statistiche_attivita_persona(me, form)

    context = {
        "storico": storico,
        "statistiche": statistiche,
        "statistiche_modulo": form,
    }

    return 'so_storico.html', context


@pagina_privata
def so_storico_excel(request, me):
    """Scarica il foglio di servizio"""
    excel = me.genera_foglio_di_servizio()
    return redirect(excel.download_url)


@pagina_pubblica
def so_scheda_informazioni(request, me=None, pk=None):
    """Mostra la scheda "Informazioni" di un servizio"""

    servizio = get_object_or_404(ServizioSO, pk=pk)
    puo_modificare = me and me.permessi_almeno(servizio, MODIFICA)

    context = {
        "attivita": servizio,
        "puo_modificare": puo_modificare,
        "me": me,
    }
    return 'so_scheda_informazioni.html', context


@pagina_privata
def so_scheda_cancella(request, me, pk):
    # todo: Gruppo WTF?! cosa fare cosa fare
    attivita = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(attivita, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if not attivita.cancellabile:
        return errore_generico(request, me, titolo="Attività non cancellabile",
                               messaggio="Questa attività non può essere cancellata.")

    titolo_messaggio = "Attività cancellata"
    testo_messaggio = "L'attività è stata cancellata con successo."
    if 'cancella-gruppo' in request.path.split('/'):
        try:
            gruppo = Gruppo.objects.get(attivita=attivita)
            gruppo.delete()
            titolo_messaggio = "Attività e gruppo cancellati"
            testo_messaggio = "L'attività e il gruppo associato sono stati cancellati con successo."
        except Gruppo.DoesNotExist:
            testo_messaggio = "L'attività è stata cancellata con successo (non esisteva un gruppo associato a quest'attività)."
    attivita.delete()

    # todo: reverse url
    return messaggio_generico(request, me, titolo=titolo_messaggio,
                              messaggio=testo_messaggio,
                              torna_titolo="Gestione attività", torna_url="/attivita/gestisci/")


@pagina_pubblica
def so_scheda_mappa(request, me=None, pk=None):
    """Mostra la scheda "Informazioni" di un servizio"""
    servizio = get_object_or_404(ServizioSO, pk=pk)
    puo_modificare = me and me.permessi_almeno(servizio, MODIFICA)
    context = {
        "attivita": servizio,
        "puo_modificare": puo_modificare,
    }
    return 'so_scheda_mappa.html', context


@pagina_privata
def so_scheda_turni(request, me=None, pk=None, pagina=None):
    """Mostra la scheda "Informazioni" di un servizio"""

    if False:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(ServizioSO, pk=pk)

    if pagina is None:
        pagina = "/attivita/scheda/%d/turni/%d/" % (attivita.pk, attivita.pagina_turni_oggi())
        return redirect(pagina)

    turni = attivita.turni.all()

    puo_modificare = me and me.permessi_almeno(attivita, MODIFICA)

    evidenzia_turno = TurnoSO.objects.get(pk=request.GET['evidenzia_turno']) \
        if 'evidenzia_turno' in request.GET else None

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(turni, TurnoSO.PER_PAGINA)
    pg = p.page(pagina)

    context = {
        'pagina': pagina,
        'pagine': p.num_pages,
        'totale': p.count,
        'turni': pg.object_list,
        'ha_precedente': pg.has_previous(),
        'ha_successivo': pg.has_next(),
        'pagina_precedente': pagina-1,
        'pagina_successiva': pagina+1,
        "attivita": attivita,
        "puo_modificare": puo_modificare,
        "evidenzia_turno": evidenzia_turno,
    }
    return 'so_scheda_turni.html', context


@pagina_privata
def so_scheda_turni_nuovo(request, me=None, pk=None):
    """Pagina di creazione di un nuovo turno"""

    attivita = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        redirect(ERRORE_PERMESSI)

    tra_una_settimana = timezone.now() + timedelta(days=7)
    tra_una_settimana_e_una_ora = tra_una_settimana + timedelta(hours=1)

    form = CreazioneTurnoForm(request.POST or None, initial={
      "inizio": tra_una_settimana, "fine": tra_una_settimana_e_una_ora,
    })
    modulo_ripeti = RipetiTurnoForm(request.POST or None, prefix="ripeti")

    if form.is_valid():
        turno = form.save(commit=False)
        turno.attivita = attivita
        turno.save()

        if request.POST.get('ripeti', default="no") == 'si' and modulo_ripeti.is_valid():
            numero_ripetizioni = modulo_ripeti.cleaned_data['numero_ripetizioni']

            giorni = modulo_ripeti.cleaned_data['giorni']
            giorni_ripetuti = 0
            giorni_nel_futuro = 1

            while giorni_ripetuti < numero_ripetizioni:

                ripetizione = TurnoSO(
                    attivita=attivita,
                    inizio=turno.inizio + timedelta(days=giorni_nel_futuro),
                    fine=turno.fine + timedelta(days=giorni_nel_futuro),
                    prenotazione=turno.prenotazione + timedelta(days=giorni_nel_futuro),
                    minimo=turno.minimo,
                    massimo=turno.massimo,
                    nome=turno.nome,
                )

                if str(ripetizione.inizio.weekday()) in giorni:
                    giorni_ripetuti += 1
                    ripetizione.save()

                giorni_nel_futuro += 1

            pass

        return redirect(turno.url)


    context = {
        "modulo": form,
        "modulo_ripeti": modulo_ripeti,
        "attivita": attivita,
        "puo_modificare": True
    }
    return 'so_scheda_turni_nuovo.html', context


@pagina_privata
def so_scheda_turni_turno_cancella(request, me, pk=None, turno_pk=None):
    turno = TurnoSO.objects.get(pk=turno_pk)
    attivita = turno.attivita
    if not me.permessi_almeno(attivita, MODIFICA):
        redirect(ERRORE_PERMESSI)

    precedente = attivita.turni.all().filter(inizio__lt=turno.inizio).order_by('inizio').last()
    if precedente:
        url_torna = precedente.url_modifica
    else:
        url_torna = attivita.url_turni_modifica

    turno.delete()
    return redirect(url_torna)


@pagina_privata
def so_scheda_turni_partecipa(request, me, pk=None, turno_pk=None):
    """ Mostra la scheda "Informazioni" di un servizio"""

    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    stato = turno.persona(me)

    if stato not in turno.TURNO_PUOI_PARTECIPARE:
        return errore_generico(request, me, titolo="Non puoi partecipare a questo turno",
                               messaggio="Siamo spiacenti, ma ci risulta che tu non possa "
                                         "richiedere partecipazione a questo turno. Vai "
                                         "all'elenco dei turni per maggiori informazioni "
                                         "sulla motivazione. ",
                               torna_titolo="Turni dell'attività",
                               torna_url=turno.url,
                               )

    p = PartecipazioneSO(
        turno=turno,
        persona=me,
    )
    p.save()
    p.richiedi()

    return messaggio_generico(request, me, titolo="Ottimo! Richiesta inoltrata.",
                              messaggio="La tua richiesta è stata inoltrata ai referenti di "
                                        "questa attività, che potranno confermarla o negarla. "
                                        "Ti manderemo una e-mail non appena risponderanno alla "
                                        "tua richiesta. Puoi sempre controllare lo stato delle tue"
                                        "richieste di partecipazione da 'Attivita' > 'I miei turni'. ",
                              torna_titolo="Vai a 'I miei turni'",
                              torna_url="/attivita/storico/")


@pagina_privata
def so_scheda_turni_ritirati(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    stato = turno.persona(me)

    if stato != turno.TURNO_PRENOTATO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente dell'attività, che potrà valutare "
                                         "la situazione e rimuoverti dai partecipanti.",
                               torna_titolo="Torna al turno",
                               torna_url=turno.url)

    partecipazione = PartecipazioneSO.con_esito_pending(turno=turno, persona=me).first()
    if not partecipazione:
        raise ValueError("TURNO_PRENOTATO_PUOI_RITIRARTI assegnato, ma nessuna partecipazione"
                         "trovata. ")

    partecipazione.autorizzazioni_ritira()
    return messaggio_generico(request, me, titolo="Richiesta ritirata.",
                              messaggio="La tua richiesta di partecipazione a questo turno "
                                        "è stata ritirata con successo.",
                              torna_titolo="Torna al turno",
                              torna_url=turno.url)


@pagina_privata
def so_scheda_turni_partecipanti(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    if not me.permessi_almeno(turno.attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    elenco = ElencoPartecipantiTurno(turno.queryset_modello())
    context = {
        "attivita": turno.attivita,
        "turno": turno,
        "elenco": elenco,
        "puo_modificare": True
    }
    return "so_scheda_turni_elenco.html", context


@pagina_privata
def so_scheda_partecipanti(request, me, pk=None):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    elenco = ElencoPartecipantiAttivita(servizio.queryset_modello())
    context = {
        "attivita": servizio,
        "elenco": elenco,
        "puo_modificare": True
    }
    return "so_scheda_partecipanti.html", context


@pagina_privata
def so_scheda_turni_rimuovi(request, me, pk=None, turno_pk=None, partecipante_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    stato = turno.persona(me)

    if stato != turno.TURNO_PRENOTATO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente dell'attività, che potrà valutare "
                                         "la situazione e rimuoverti dai partecipanti.",
                               torna_titolo="Torna al turno",
                               torna_url=turno.url)

    partecipazione = PartecipazioneSO.con_esito_pending(turno=turno,
                                                       persona=me).first()
    if not partecipazione:
        raise ValueError("TURNO_PRENOTATO_PUOI_RITIRARTI assegnato, ma nessuna partecipazione"
                         "trovata. ")

    partecipazione.autorizzazioni_ritira()
    return messaggio_generico(request, me, titolo="Richiesta ritirata.",
                              messaggio="La tua richiesta di partecipazione a questo turno "
                                        "è stata ritirata con successo.",
                              torna_titolo="Torna al turno",
                              torna_url=turno.url)


@pagina_privata
def so_scheda_turni_link_permanente(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    attivita = turno.attivita
    pagina = turno.elenco_pagina()

    # todo: reverse url
    return redirect("/attivita/scheda/%d/turni/%d/?evidenzia_turno=%d#turno-%d" % (
        attivita.pk, pagina, turno.pk, turno.pk,
    ))


@pagina_privata
def so_scheda_turni_modifica_link_permanente(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    attivita = turno.attivita
    pagina = turno.elenco_pagina()

    # todo: reverse url
    return redirect("/attivita/scheda/%d/turni/modifica/%d/?evidenzia_turno=%d#turno-%d" % (
        attivita.pk, pagina, turno.pk, turno.pk
    ))


@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def so_scheda_informazioni_modifica(request, me, pk=None):
    attivita = get_object_or_404(ServizioSO, pk=pk)
    apertura_precedente = attivita.apertura

    if not me.permessi_almeno(attivita, MODIFICA):
        if me.permessi_almeno(attivita, MODIFICA, solo_deleghe_attive=False):
            # Se la mia delega e' sospesa per l'attivita', vai in prima pagina
            #  per riattivarla.
            return redirect(attivita.url)

        return redirect(ERRORE_PERMESSI)

    if request.POST and not me.ha_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE):
        request.POST = request.POST.copy()
        request.POST['centrale_operativa'] = attivita.centrale_operativa

    form = AttivitaInformazioniForm(request.POST or None, instance=attivita)
    form.fields['estensione'].queryset = attivita.sede.get_ancestors(include_self=True).exclude(estensione=NAZIONALE)

    if not me.ha_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE):
        form.fields['centrale_operativa'].widget.attrs['disabled'] = True

    if form.is_valid():
        form.save()

        # Se e' stato cambiato lo stato dell'attivita'
        attivita.refresh_from_db()
        if attivita.apertura != apertura_precedente:

            if attivita.apertura == attivita.APERTA:
                attivita.riapri()

            else:
                attivita.chiudi(autore=me)

    context = {
        "attivita": attivita,
        "puo_modificare": True,
        "modulo": form,
    }

    return 'so_scheda_informazioni_modifica.html', context


@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def so_riapri(request, me, pk=None):
    """Riapre il servizio """
    servizio = get_object_or_404(ServizioSO, pk=pk)

    if not me.permessi_almeno(servizio, MODIFICA, solo_deleghe_attive=False):
        return redirect(ERRORE_PERMESSI)

    servizio.riapri(invia_notifiche=True)
    return redirect(servizio.url)


@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def so_scheda_turni_modifica(request, me, pk=None, pagina=None):
    """
    Mostra la pagina di modifica di una attivita'.
    """

    attivita = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):

        if me.permessi_almeno(attivita, MODIFICA, solo_deleghe_attive=False):
            # Se la mia delega e' sospesa per l'attivita', vai in prima pagina
            #  per riattivarla.
            return redirect(attivita.url)

        return redirect(ERRORE_PERMESSI)

    if pagina is None:
        pagina = "/attivita/scheda/%d/turni/modifica/%d/" % (attivita.pk, attivita.pagina_turni_oggi())
        return redirect(pagina)

    turni = attivita.turni.all()

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(turni, TurnoSO.PER_PAGINA)
    pg = p.page(pagina)

    moduli = []
    moduli_aggiungi_partecipanti = []
    turni = pg.object_list
    for turno in turni:
        modulo = ModificaTurnoForm(request.POST or None,
                                     instance=turno,
                                     prefix="turno_%d" % (turno.pk,))
        moduli += [modulo]

        modulo_aggiungi_partecipanti = AggiungiPartecipantiForm(request.POST or
                                                            None,
                                                                  prefix="turno_agg_%d" % (turno.pk,))
        moduli_aggiungi_partecipanti += [modulo_aggiungi_partecipanti]

        if modulo.is_valid():
            modulo.save()

        if modulo_aggiungi_partecipanti.is_valid():

            # Aggiungi partecipante.
            for partecipante in modulo_aggiungi_partecipanti.cleaned_data['persone']:
                turno.aggiungi_partecipante(partecipante, richiedente=me)

            redirect(turno.url_modifica)

    # Salva e aggiorna le presenze.
    for chiave, valore in request.POST.items():
        if "presenza-" in chiave:
            p_pk = int(chiave.replace("presenza-", ""))
            p_si = '1' in valore
            pa = PartecipazioneSO.objects.get(pk=p_pk)
            pa.stato = PartecipazioneSO.RICHIESTA if p_si else \
                PartecipazioneSO.NON_PRESENTATO
            pa.save()

    turni_e_moduli = zip(turni, moduli, moduli_aggiungi_partecipanti)

    evidenzia_turno = TurnoSO.objects.get(pk=request.GET['evidenzia_turno']) \
        if 'evidenzia_turno' in request.GET else None

    context = {
        'pagina': pagina,
        'pagine': p.num_pages,
        'totale': p.count,
        'turni': turni_e_moduli,
        'ha_precedente': pg.has_previous(),
        'ha_successivo': pg.has_next(),
        'pagina_precedente': pagina-1,
        'pagina_successiva': pagina+1,
        "attivita": attivita,
        "puo_modificare": True,
        "url_modifica": '/modifica',
        "evidenzia_turno": evidenzia_turno,
    }

    return 'so_scheda_turni_modifica.html', context


@pagina_privata
def so_scheda_partecipazione_cancella(request, me, pk, partecipazione_pk):
    partecipazione = get_object_or_404(PartecipazioneSO, pk=partecipazione_pk)

    if not me.permessi_almeno(partecipazione.turno.attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    turno = partecipazione.turno
    partecipazione.delete()
    return redirect(turno.url_modifica)


@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def so_scheda_report(request, me, pk=None):
    """Mostra la pagina di modifica di un servizio"""
    if False:
        return ci_siamo_quasi(request, me)

    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if request.POST:
        return servizio.genera_report(format=ServizioSO.REPORT_FORMAT_EXCEL)

    context = {
        "attivita": servizio,
        "puo_modificare": True,
    }
    return 'so_scheda_report.html', context


@pagina_privata
def so_statistiche(request, me):
    sedi = me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE)

    form = StatisticheAttivitaForm(request.POST or None, initial={"sedi":sedi})
    form.fields['sedi'].queryset = sedi

    statistiche = []
    chart = {}

    periodi = 12

    if form.is_valid():
        oggi = date.today()

        giorni = int(form.cleaned_data['periodo'])
        if giorni == form.SETTIMANA:
            etichetta = "sett."
        elif giorni == form.QUINDICI_GIORNI:
            etichetta = "fortn."
        elif giorni == form.MESE:
            etichetta = "mesi"
        else:
            raise ValueError("Etichetta mancante.")

        for periodo in range(periodi, 0, -1):

            dati = {}

            fine = oggi - timedelta(days=(giorni*periodo))
            inizio = fine - timedelta(days=giorni-1)

            fine = datetime.combine(fine, time(23, 59, 59))
            inizio = datetime.combine(inizio, time(0, 0, 0))

            dati['inizio'] = inizio
            dati['fine'] = fine

            # Prima, ottiene tutti i queryset.
            qs_attivita = ServizioSO.objects.filter(stato=ServizioSO.VISIBILE,
                                                   sede__in=sedi)
            qs_turni = TurnoSO.objects.filter(attivita__in=qs_attivita,
                                             inizio__lte=fine, fine__gte=inizio)
            qs_part = PartecipazioneSO.con_esito_ok(turno__in=qs_turni)

            ore_di_servizio = qs_turni.annotate(durata=F('fine') - F('inizio')).aggregate(totale_ore=Sum('durata'))['totale_ore'] or timedelta()
            ore_uomo_di_servizio = qs_part.annotate(durata=F('turno__fine') - F('turno__inizio')).aggregate(totale_ore=Sum('durata'))['totale_ore'] or timedelta()

            # Poi, associa al dizionario statistiche.
            dati['etichetta'] = "%d %s fa" % (periodo, etichetta,)
            dati['num_turni'] = qs_turni.count()
            dati['ore_di_servizio'] = ore_di_servizio
            dati['ore_uomo_di_servizio'] = ore_uomo_di_servizio
            try:
                dati['rapporto'] = round(ore_uomo_di_servizio / ore_di_servizio, 3)
            except ZeroDivisionError:
                dati['rapporto'] = 0

            statistiche.append(dati)

        chart['labels'] = json.dumps([x['etichetta'] for x in statistiche])
        chart['num_turni'] = json.dumps([x['num_turni'] for x in statistiche])
        chart['ore_di_servizio'] = json.dumps([timedelta_ore(x['ore_di_servizio']) for x in statistiche])
        chart['ore_uomo_di_servizio'] = json.dumps([timedelta_ore(x['ore_uomo_di_servizio']) for x in statistiche])
        chart['rapporto'] = json.dumps([x['rapporto'] for x in statistiche])

    context = {
        "modulo": form,
        "statistiche": statistiche,
        "chart": chart,
    }
    return 'so_statistiche.html', context
