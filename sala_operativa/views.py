import calendar
import json
from datetime import date, timedelta, datetime, time

from django.db.models import Count, F, Sum
from django.utils import timezone
from django.utils.timezone import now
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, get_object_or_404, HttpResponse
from django.utils.safestring import mark_safe

from anagrafica.costanti import NAZIONALE, LOCALE, PROVINCIALE, REGIONALE
from anagrafica.permessi.applicazioni import REFERENTE_SERVIZI_SO, REFERENTE_OPERAZIONE_SO, REFERENTE_FUNZIONE_SO
from anagrafica.permessi.costanti import (MODIFICA, COMPLETO, ERRORE_PERMESSI,
                                          GESTIONE_SO_SEDE, GESTIONE_SERVIZI, GESTIONE_REFERENTI_SO,
                                          GESTIONE_OPERAZIONI, GESTIONE_REFERENTI_OPERAZIONI_SO, GESTIONE_FUNZIONI,
                                          GESTIONE_REFERENTI_FUNZIONI_SO, )
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico, messaggio_generico, errore_no_volontario
from base.utils import poco_fa, timedelta_ore
from posta.models import Messaggio
from .utils import turni_raggruppa_giorno
from .models import PartecipazioneSO, ServizioSO, TurnoSO, ReperibilitaSO, MezzoSO, PrenotazioneMMSO, DatoreLavoro, \
    OperazioneSO, FunzioneSO
from .elenchi import ElencoPartecipantiTurno, ElencoPartecipantiAttivita
from .forms import (ModificaServizioForm, ModificaTurnoForm, StatisticheServiziForm,
                    AggiungiPartecipantiForm, CreazioneTurnoForm, RipetiTurnoForm,
                    VolontarioReperibilitaForm, AggiungiReperibilitaPerVolontarioForm,
                    OrganizzaServizioReferenteForm, OrganizzaServizioForm, CreazioneMezzoSO,
                    AbbinaMezzoMaterialeForm, VolontarioReperibilitaModelForm,
                    ModuloProfiloModificaAnagraficaDatoreLavoro, OrganizzaOperazioneReferenteForm,
                    OrganizzaOperazioneForm, OrganizzaFunzioneReferenteForm, OrganizzaFunzioneForm)
from django.contrib import messages

INITIAL_INIZIO_FINE_PARAMS = {
    "inizio": poco_fa() + timedelta(hours=1),
    "fine": poco_fa() + timedelta(hours=2),
}


@pagina_privata
def so_index(request, me):
    if not me.volontario:
        return redirect('/')

    context = {
        'ora': poco_fa(),
    }

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    servizi_dove_referente = me.oggetti_permesso(GESTIONE_SERVIZI)

    if sedi or servizi_dove_referente:
        context.update({
            'ora': poco_fa(),
            'sedi': sedi,
            'reperibilita': ReperibilitaSO.reperibilita_per_sedi(sedi),
        })
    else:
        return redirect(reverse('so:reperibilita'))
    return 'sala_operativa_index.html', context


@pagina_privata
def so_reperibilita(request, me):
    form = VolontarioReperibilitaForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
    form.fields['datore_lavoro'].choices = VolontarioReperibilitaForm.popola_datore(me)

    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            if cd['inizio'] < datetime.now():
                messages.warning(request, 'Attenzione! la data di inizio inserita è precedente a quella corrente.')
            for estensione in cd['estensione']:
                reperibilita = ReperibilitaSO(
                    estensione=estensione,
                    inizio=cd['inizio'],
                    fine=cd['fine'],
                    attivazione=cd['attivazione'],
                    applicazione_bdl=cd['applicazione_bdl'],
                    persona=me,
                    creato_da=me,
                )
                if cd['applicazione_bdl']:
                    reperibilita.datore_lavoro = DatoreLavoro.objects.get(pk=cd['datore_lavoro'])
                reperibilita.save()
            return redirect(reverse('so:reperibilita'))

    reperibilita = ReperibilitaSO.reperibilita_di(me)

    context = {
        'me': me,
        'form': form,
        'reperibilita_n': reperibilita.filter(estensione=NAZIONALE)[:50],
        'reperibilita_r': reperibilita.filter(estensione=REGIONALE)[:50],
        'reperibilita_p': reperibilita.filter(estensione=PROVINCIALE)[:50],
        'reperibilita_l': reperibilita.filter(estensione=LOCALE)[:50],
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
    return redirect(reverse('so:reperibilita'))


@pagina_privata
def so_reperibilita_edit(request, me, pk):
    if not me.volontario:
        return redirect('/')

    reperibilita = get_object_or_404(ReperibilitaSO, pk=pk)
    if reperibilita.creato_da != me:
        return redirect(ERRORE_PERMESSI)

    form = VolontarioReperibilitaModelForm(request.POST or None, instance=reperibilita)
    form.fields['datore_lavoro'].queryset = DatoreLavoro.objects.filter(persona=me)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('so:reperibilita'))

    context = {
        'form': form,
        'reperibilita': reperibilita,
    }
    return 'sala_operativa_reperibilita_edit.html', context


@pagina_privata
def so_reperibilita_backup(request, me):
    form = AggiungiReperibilitaPerVolontarioForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
    form.fields['datore_lavoro'].choices = VolontarioReperibilitaForm.popola_datore(me)

    creati_da = []

    for sede in me.oggetti_permesso(GESTIONE_SO_SEDE, solo_deleghe_attive=False):
        creati_da.append(sede.presidente())
        creati_da.extend(list(sede.commissari()))
        creati_da.extend(list(sede.commissari()))
        creati_da.extend(list(sede.obbiettivo_3()))
        creati_da.extend(list(sede.delegati_so()))

    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            if cd['inizio'] < datetime.now():
                messages.warning(request, 'Attenzione! la data di inizio inserita è precedente a quella corrente.')
            for estensione in cd['estensione']:
                reperibilita = ReperibilitaSO(
                    estensione=estensione,
                    inizio=cd['inizio'],
                    fine=cd['fine'],
                    attivazione=cd['attivazione'],
                    applicazione_bdl=cd['applicazione_bdl'],
                    persona=cd['persona'],
                    creato_da=me,
                )
                if cd['applicazione_bdl']:
                    reperibilita.datore_lavoro = DatoreLavoro.objects.get(pk=cd['datore_lavoro'])
                reperibilita.save()
            return redirect(reverse('so:reperibilita_backup'))

    reperibilita = ReperibilitaSO.reperibilita_creati_da(creati_da)
    context = {
        'form': form,
        'reperibilita_n': reperibilita.filter(estensione=NAZIONALE),
        'reperibilita_r': reperibilita.filter(estensione=REGIONALE),
        'reperibilita_p': reperibilita.filter(estensione=PROVINCIALE),
        'reperibilita_l': reperibilita.filter(estensione=LOCALE),
    }
    return 'sala_operativa_reperibilita.html', context


@pagina_privata
def so_gestisci(request, me, stato="aperte"):

    servizi_tutti = me.oggetti_permesso(GESTIONE_SERVIZI, solo_deleghe_attive=False)
    print(servizi_tutti)
    servizi_aperti = servizi_tutti.filter(apertura=ServizioSO.APERTA)
    servizi_chiusi = servizi_tutti.filter(apertura=ServizioSO.CHIUSA)

    servizi = servizi_aperti if stato == "aperte" else servizi_chiusi
    servizi = servizi.order_by('-inizio', ).annotate(num_turni=Count('turni_so'))

    context = {
        "stato": stato,
        "servizi_n": servizi.filter(estensione__estensione=NAZIONALE),
        "servizi_l": servizi.filter(estensione__estensione=LOCALE),
        "servizi_p": servizi.filter(estensione__estensione=PROVINCIALE),
        "servizi_r": servizi.filter(estensione__estensione=REGIONALE),
        "servizi_aperti": servizi_aperti.count(),
        "servizi_chiusi": servizi_chiusi.count(),
        "servizio_referenti_modificabili": me.oggetti_permesso(GESTIONE_REFERENTI_SO),
    }
    return 'so_gestisci.html', context


@pagina_privata
def so_organizza(request, me):
    from anagrafica.models import Persona

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not sedi:
        messages.error(request, 'Non hai sedi con la delega SO.')
        return redirect(reverse('so:index'))

    form_referente = OrganizzaServizioReferenteForm(request.POST or None)
    form = OrganizzaServizioForm(request.POST or None)
    form.fields['sede'].queryset = sedi

    if form.is_valid() and form_referente.is_valid():
        cd = form.cleaned_data
        form_referente_cd = form_referente.cleaned_data

        servizio = form.save(commit=False)
        servizio.sede = cd['sede']
        servizio.estensione = cd['sede'].comitato
        servizio.save()

        if form_referente_cd['scelta'] == form_referente.SONO_IO:
            # Io sono il referente.
            servizio.aggiungi_delegato(REFERENTE_SERVIZI_SO, me, firmatario=me, inizio=poco_fa())
            return redirect(servizio.url_modifica)

        elif form_referente_cd['scelta'] == form_referente.SCEGLI_REFERENTI:
            # Il referente è qualcun altro.
            return redirect(reverse('so:organizza_referenti', args=[servizio.pk, ]))

        else:
            persona = Persona.objects.get(pk=form_referente_cd['scelta'])
            servizio.aggiungi_delegato(REFERENTE_SERVIZI_SO, persona, firmatario=me, inizio=poco_fa())
            return redirect(servizio.url_modifica)

    context = {
        "modulo": form,
        "modulo_referente": form_referente,
    }
    return 'so_organizza.html', context


@pagina_privata
def so_organizza_fatto(request, me, pk=None):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    return messaggio_generico(request, me,
        titolo="Servizio organizzato",
        messaggio="Abbiamo inviato un messaggio ai referenti che hai selezionato. "
                  "Appena accederanno a Gaia, gli chiederemo di darci maggiori informazioni sul servizio, "
                  "come gli orari dei turni e l'indirizzo.",
        torna_titolo="Torna a Gestione Servizi",
        torna_url=reverse('so:gestisci'))


@pagina_privata
def so_organizza_operazione_fatto(request, me, pk=None):
    operazione = get_object_or_404(OperazioneSO, pk=pk)
    if not me.permessi_almeno(operazione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    return messaggio_generico(request, me,
        titolo="Operazione organizzato",
        messaggio="Abbiamo inviato un messaggio ai referenti che hai selezionato. "
                  "Appena accederanno a Gaia, gli chiederemo di darci maggiori informazioni sull'operazione, "
                  "come gli orari dei turni e l'indirizzo.",
        torna_titolo="Torna a Organizza operazione",
        torna_url=reverse('so:gestisce_operazione'))


@pagina_privata
def so_referenti(request, me, pk=None, nuova=False):
    servizio = get_object_or_404(ServizioSO, pk=pk)

    if not me.permessi_almeno(servizio, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    delega = REFERENTE_SERVIZI_SO

    if nuova:
        continua_url = reverse('so:organizza_fatto', args=[servizio.pk,])
    else:
        continua_url = reverse('so:gestisci')

    context = {
        "delega": delega,
        "servizio": servizio,
        "continua_url": continua_url
    }
    return 'so_referenti.html', context


@pagina_privata
def so_referenti_operazione(request, me, pk=None, nuova=False):
    operazione = get_object_or_404(OperazioneSO, pk=pk)

    if not me.permessi_almeno(operazione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    delega = REFERENTE_OPERAZIONE_SO

    if nuova:
        continua_url = reverse('so:organizza_operazione_fatto', args=[operazione.pk,])
    else:
        continua_url = reverse('so:gestisce_operazione')

    context = {
        "delega": delega,
        "servizio": operazione,
        "continua_url": continua_url
    }
    return 'so_referenti.html', context



@pagina_privata
def so_calendario(request, me=None):
    """Mostra il calendario dei turni nei servizi"""
    from .utils import CalendarTurniSO

    if not me.volontario:
        return errore_no_volontario(request, me)

    current_month = timezone.now().today()
    year = now().year
    month = now().month

    # Navigazione mesi
    current_month_get = request.GET.get('m')
    if current_month_get:
        try:
            year, month = [int(i) for i in current_month_get.split('-')]
            current_month = datetime(year=year, month=month, day=1)
        except:
            pass

    # Lavorazione date
    _, num_days = calendar.monthrange(year, month)
    inizio_mese = current_month.replace(day=1, hour=0, minute=0, second=0)
    fine_mese = inizio_mese.replace(day=num_days) + timedelta(days=1)

    # Estrazione dei turni
    turni = TurnoSO.calendario_di(me, inizio_mese, fine_mese)

    # Lavorazione calendario
    calendario = CalendarTurniSO(current_month, turni)
    malendario_mensile_html = calendario.formatmonth(withyear=True)

    context = {
        "inizio": inizio_mese,
        "fine": fine_mese,
        "turni": turni,
        'calendario': mark_safe(malendario_mensile_html),
        'next_month': CalendarTurniSO.next_month(inizio_mese),
        'prev_month': CalendarTurniSO.prev_month(inizio_mese),
    }
    return 'so_calendar.html', context


# @pagina_privata
# def so_calendario_old(request, me=None, inizio=None, fine=None, vista="calendario"):
#     """Mostra il calendario dei turni nei servizi"""
#     if not me.volontario:
#         return errore_no_volontario(request, me)
#
#     # Range default e massimo
#     DEFAULT_GIORNI = 6
#     MASSIMO_GIORNI = 31
#
#     # Formato date URL
#     FORMATO = "%d-%m-%Y"
#
#     if inizio is None:
#         inizio = date.today().strftime(FORMATO)
#
#     inizio = datetime.strptime(inizio, FORMATO).date()
#
#     if fine is None:
#         fine = inizio + timedelta(DEFAULT_GIORNI)
#     else:
#         fine = datetime.strptime(fine, FORMATO).date()
#
#     # Assicura che il range sia valido (non troppo breve, non troppo lungo)
#     differenza = (fine - inizio)
#     if differenza.days < 0 or differenza.days > MASSIMO_GIORNI:
#         return so_calendario(request, me, inizio=inizio, fine=None)
#
#     # Successivo
#     successivo_inizio = inizio + differenza
#     successivo_inizio_stringa = successivo_inizio.strftime(FORMATO)
#     successivo_fine = fine + differenza
#     successivo_fine_stringa = successivo_fine.strftime(FORMATO)
#
#     successivo_url = reverse('so:calendario_con_range', args=[successivo_inizio_stringa,
#                                                               successivo_fine_stringa,])
#
#     # Oggi
#     oggi_url = reverse('so:calendario')
#
#     # Precedente
#     precedente_inizio = inizio - differenza
#     precedente_inizio_stringa = precedente_inizio.strftime(FORMATO)
#     precedente_fine = fine - differenza
#     precedente_fine_stringa = precedente_fine.strftime(FORMATO)
#
#     precedente_url = reverse('so:calendario_con_range', args=[precedente_inizio_stringa,
#                                                               precedente_fine_stringa,])
#
#     # Elenco
#     turni = TurnoSO.calendario_di(me, inizio, fine)
#     raggruppati = turni_raggruppa_giorno(turni)
#
#     context = {
#         "inizio": inizio,
#         "fine": fine,
#
#         "successivo_inizio": successivo_inizio,
#         "successivo_fine": successivo_fine,
#         "successivo_url": successivo_url,
#
#         "oggi_url": oggi_url,
#
#         "precedente_inizio": precedente_inizio,
#         "precedente_fine": precedente_fine,
#         "precedente_url": precedente_url,
#
#         "turni": turni,
#         "raggruppati": raggruppati,
#     }
#     return 'so_calendario.html', context


@pagina_privata
def so_storico(request, me):
    """Mostra uno storico dei servizi a cui ha partecipato"""

    storico = PartecipazioneSO.objects.filter(reperibilita__persona=me).order_by('-turno__inizio')

    context = {
        "storico": storico,
    }

    return 'so_storico.html', context


@pagina_privata
def so_storico_excel(request, me):
    """Scarica il foglio di servizio"""
    excel = me.genera_foglio_di_servizio()
    return redirect(excel.download_url)


@pagina_pubblica
def so_scheda_informazioni(request, me=None, pk=None):
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
    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if not servizio.cancellabile:
        return errore_generico(request, me,
                               titolo="Servizio non cancellabile",
                               messaggio="Questa servizio non può essere cancellato")

    titolo_messaggio = "Servizio cancellato"
    testo_messaggio = "Il Servizio è stato cancellato con successo."

    servizio.delete()

    return messaggio_generico(request, me,
                              titolo=titolo_messaggio,
                              messaggio=testo_messaggio,
                              torna_titolo="Gestione servizio",
                              torna_url=reverse('so:gestisci'), )


@pagina_pubblica
def so_scheda_mm(request, me=None, pk=None):
    """Mostra la scheda "Mezzi/materiali" di un servizio"""

    servizio = get_object_or_404(ServizioSO, pk=pk)
    puo_modificare = me and me.permessi_almeno(servizio, MODIFICA)
    mie_sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)

    if not puo_modificare:
        messages.error(request, 'Non hai dei permessi necessari per modificare questo oggetto.')
        return redirect(reverse('so:index'))

    context = {
        "attivita": servizio,
        "prenotazioni": PrenotazioneMMSO.del_servizio(servizio),
        "mezzi_disponibili": MezzoSO.disponibili_per_sedi(mie_sedi),
        "puo_modificare": puo_modificare,
        "me": me,
    }

    return 'so_scheda_mm.html', context


@pagina_pubblica
def so_scheda_mm_abbina(request, me=None, pk=None, mm_pk=None):
    """Mostra la scheda di abbinamento mezzi materiali """

    servizio = get_object_or_404(ServizioSO, pk=pk)
    mezzo = get_object_or_404(MezzoSO, pk=mm_pk)

    tra_un_ora = now() + timedelta(hours=1)

    form = AbbinaMezzoMaterialeForm(request.POST or None,
                                    instance=mezzo,
                                    initial={'inizio': tra_un_ora})

    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            nuova_prenotazione = PrenotazioneMMSO(servizio=servizio,
                                                  mezzo=mezzo,
                                                  inizio=cd['inizio'],
                                                  fine=cd['fine'],)
            nuova_prenotazione.save()

            tipo = nuova_prenotazione.mezzo.get_tipo_display().lower()
            messages.success(request, 'Il %s è stato prenotato con successo.' % tipo)

            return redirect(reverse('so:scheda_mm', args=[pk, ]))

    context = {
        'form': form,
        'attivita': servizio,
        'mezzo': mezzo,
        'puo_modificare': True,
    }

    return 'so_scheda_mm_abbina.html', context


@pagina_pubblica
def so_scheda_mm_cancella(request, me=None, pk=None, prenotazione=None):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    prenotazione = get_object_or_404(PrenotazioneMMSO, pk=prenotazione)
    prenotazione.delete()

    return redirect(reverse('so:scheda_mm', args=[pk, ]))


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
    """ Mostra la scheda "Informazioni" di un servizio. """
    servizio = get_object_or_404(ServizioSO, pk=pk)
    turni = servizio.turni_so.all()

    puo_modificare = me and me.permessi_almeno(servizio, MODIFICA)

    if pagina is None:
        pagina = reverse('so:servizio_turni_pagina', args=[servizio.pk, servizio.pagina_turni_oggi()])
        return redirect(pagina)

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
        "attivita": servizio,
        "puo_modificare": puo_modificare,
        "evidenzia_turno": evidenzia_turno,
    }
    return 'so_scheda_turni.html', context


@pagina_privata
def so_scheda_turni_nuovo(request, me=None, pk=None):
    """Pagina di creazione di un nuovo turno"""

    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, MODIFICA):
        redirect(ERRORE_PERMESSI)

    tra_una_settimana = timezone.now() + timedelta(days=7)
    tra_una_settimana_e_una_ora = tra_una_settimana + timedelta(hours=1)

    form = CreazioneTurnoForm(request.POST or None, initial={
      "inizio": tra_una_settimana, "fine": tra_una_settimana_e_una_ora,
    })
    modulo_ripeti = RipetiTurnoForm(request.POST or None, prefix="ripeti")

    if form.is_valid():
        turno = form.save(commit=False)
        turno.attivita = servizio
        turno.save()

        if request.POST.get('ripeti', default="no") == 'si' and modulo_ripeti.is_valid():
            cd = modulo_ripeti.cleaned_data
            numero_ripetizioni = cd['numero_ripetizioni']

            giorni = modulo_ripeti.cleaned_data['giorni']
            giorni_ripetuti = 0
            giorni_nel_futuro = 1

            while giorni_ripetuti < numero_ripetizioni:
                ripetizione = TurnoSO(
                    attivita=servizio,
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

        return redirect(turno.url)

    context = {
        "modulo": form,
        "modulo_ripeti": modulo_ripeti,
        "attivita": servizio,
        "puo_modificare": True
    }
    return 'so_scheda_turni_nuovo.html', context


@pagina_privata
def so_scheda_turni_turno_cancella(request, me, pk=None, turno_pk=None):
    turno = TurnoSO.objects.get(pk=turno_pk)
    servizio = turno.attivita
    if not me.permessi_almeno(servizio, MODIFICA):
        redirect(ERRORE_PERMESSI)

    precedente = servizio.turni_so.filter(inizio__lt=turno.inizio).order_by('inizio').last()
    if precedente:
        url_torna = precedente.url_modifica
    else:
        url_torna = servizio.url_turni_modifica

    turno.delete()
    return redirect(url_torna)


@pagina_privata
def so_scheda_turni_ritirati(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    stato = turno.persona(me)

    if stato != turno.TURNO_PRENOTATO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente del servizio, che potrà valutare "
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
        return errore_generico(request, me,
                               titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente dell'attività, che potrà valutare "
                                         "la situazione e rimuoverti dai partecipanti.",
                               torna_titolo="Torna al turno",
                               torna_url=turno.url)

    partecipazione = PartecipazioneSO.con_esito_pending(turno=turno, persona=me).first()
    if not partecipazione:
        raise ValueError("TURNO_PRENOTATO_PUOI_RITIRARTI assegnato, ma nessuna partecipazione trovata.")

    partecipazione.autorizzazioni_ritira()
    return messaggio_generico(request, me, titolo="Richiesta ritirata.",
                              messaggio="La tua richiesta di partecipazione a questo turno "
                                        "è stata ritirata con successo.",
                              torna_titolo="Torna al turno",
                              torna_url=turno.url)


@pagina_privata
def so_scheda_turni_permalink(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    servizio = turno.attivita
    pagina = turno.elenco_pagina()

    return redirect(reverse('so:servizio_turni_pagina', args=[servizio.pk, pagina, ]) +
                            "?evidenzia_turno=%d#turno-%d" % (turno.pk, turno.pk))


@pagina_privata
def so_scheda_turni_modifica_permalink(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    servizio = turno.attivita
    pagina = turno.elenco_pagina()

    return redirect(reverse('so:servizio_turni_modifica_pagina', args=[servizio.pk, pagina, ]) +
                            "?evidenzia_turno=%d#turno-%d" % (turno.pk, turno.pk))


@pagina_privata
def so_turno_abbina_volontario(request, me, turno_pk, reperibilita_pk):
    turno = get_object_or_404(TurnoSO, pk=turno_pk)
    servizio = turno.attivita
    reperibilita = ReperibilitaSO.objects.get(pk=reperibilita_pk)
    if reperibilita.estensione != servizio.estensione.estensione:
        messages.success(request, 'La reperibilità ha una estensione diversa non può essere abbinata')
        return redirect(reverse('so:servizio_turni_modifica_link_permanente',
                                args=[servizio.pk, turno.pk, ]))

    partecipazione, created = turno.abbina_reperibilita(reperibilita)
    if created:
        messages.success(request, 'Il volontario è stato abbinato al turno.')

        Messaggio.costruisci_e_invia(
            oggetto="Abbinamento turno",
            modello="email_abbina_reperibilità.html",
            corpo={},
            mittente=me,
            destinatari=[
                partecipazione.reperibilita.persona
            ]
        )

        return redirect(reverse('so:servizio_turni_modifica_link_permanente',
                                    args=[servizio.pk, turno.pk,]))
    else:
        messages.success(request, 'Il volontario è già abbinato in questa fascia oraria')
        return redirect(reverse('so:servizio_turni_modifica_link_permanente',
                                args=[servizio.pk, turno.pk, ]))


@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_scheda_informazioni_modifica(request, me, pk=None):
    servizio = get_object_or_404(ServizioSO, pk=pk)

    apertura_precedente = servizio.apertura

    if not me.permessi_almeno(servizio, MODIFICA):
        if me.permessi_almeno(servizio, MODIFICA, solo_deleghe_attive=False):
            # Se la mia delega e' sospesa per l'attivita', vai in prima pagina per riattivarla.
            return redirect(servizio.url)
        return redirect(ERRORE_PERMESSI)

    form = ModificaServizioForm(request.POST or None, instance=servizio)

    form.fields['estensione'].queryset = servizio.sede.get_ancestors(include_self=True) if \
        me.sedi_deleghe_attuali().filter(estensione=NAZIONALE).exists() else \
        servizio.sede.get_ancestors(include_self=True).exclude(estensione=NAZIONALE)

    if form.is_valid():
        form.save()

        # Se e' stato cambiato lo stato dell'attivita'
        servizio.refresh_from_db()
        if servizio.apertura != apertura_precedente:
            if servizio.apertura == servizio.APERTA:
                servizio.riapri()
            else:
                servizio.chiudi(autore=me)

    context = {
        "me": me,
        "attivita": servizio,
        "puo_modificare": True,
        "modulo": form,
    }
    return 'so_scheda_informazioni_modifica.html', context

# todo: permesso
@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_riapri(request, me, pk=None):
    """Riapre il servizio """
    servizio = get_object_or_404(ServizioSO, pk=pk)

    if not me.permessi_almeno(servizio, MODIFICA, solo_deleghe_attive=False):
        return redirect(ERRORE_PERMESSI)

    servizio.riapri(invia_notifiche=True)
    return redirect(servizio.url)


@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_scheda_turni_modifica(request, me, pk=None, pagina=None):
    """ Mostra la pagina di modifica di un servizio """

    servizio = get_object_or_404(ServizioSO, pk=pk)
    if not me.permessi_almeno(servizio, MODIFICA):
        if me.permessi_almeno(servizio, MODIFICA, solo_deleghe_attive=False):
            # Se la mia delega è sospesa per il servizio, vai in prima pagina per riattivarlo
            return redirect(servizio.url)

        return redirect(ERRORE_PERMESSI)

    if pagina is None:
        return redirect(reverse('so:servizio_turni_modifica_pagina',
                                args=[servizio.pk, servizio.pagina_turni_oggi(),]))

    turni = servizio.turni_so.all()

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(turni, TurnoSO.PER_PAGINA)
    pg = p.page(pagina)

    forms = list()
    moduli_aggiungi_partecipanti = list()
    reperibilita_n = list()
    reperibilita_r = list()
    reperibilita_l = list()
    reperibilita_p = list()

    turni = pg.object_list
    for turno in turni:
        form = ModificaTurnoForm(request.POST or None, instance=turno, prefix="turno_%d" % turno.pk)
        forms += [form]

        modulo_aggiungi_partecipanti = AggiungiPartecipantiForm(request.POST or None,
                                                                prefix="turno_agg_%d" % turno.pk)
        moduli_aggiungi_partecipanti += [modulo_aggiungi_partecipanti]
        reperibilita = turno.trova_reperibilita()
        reperibilita_n.append(reperibilita.filter(estensione=NAZIONALE))
        reperibilita_r.append(reperibilita.filter(estensione=REGIONALE))
        reperibilita_l.append(reperibilita.filter(estensione=LOCALE))
        reperibilita_p.append(reperibilita.filter(estensione=PROVINCIALE))

        if form.is_valid():
            form.save()

        # Aggiungi partecipante (dal modal-box)
        if modulo_aggiungi_partecipanti.is_valid():
            cd = modulo_aggiungi_partecipanti.cleaned_data
            for reperibilita_trovata in cd['persone']:
                turno.aggiungi_partecipante(reperibilita_trovata)

            messages.success(request, 'I partecipanti selezionati sono stati abbinati al turno con successo.')
            return redirect(turno.url_modifica)

    turni_e_moduli = zip(
        turni,
        forms,
        moduli_aggiungi_partecipanti,
        reperibilita_n,
        reperibilita_r,
        reperibilita_l,
        reperibilita_p
    )

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
        "attivita": servizio,
        "puo_modificare": True,
        "url_modifica": '/modifica',
        "evidenzia_turno": evidenzia_turno,
    }

    return 'so_scheda_turni_modifica.html', context


@pagina_privata
def so_scheda_partecipazione_cancella(request, me, turno_pk, partecipazione_pk):
    partecipazione = get_object_or_404(PartecipazioneSO, pk=partecipazione_pk)

    if not me.permessi_almeno(partecipazione.turno.attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    turno = partecipazione.turno
    partecipazione.delete()

    messages.success(request, 'La reperibilità è stata disabbinata dal turno.')
    return redirect(turno.url_modifica)

# todo: permesso
# todo: adeguamento report
@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_scheda_report(request, me, pk=None):
    """Mostra la pagina di modifica di un servizio"""
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
    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)

    form = StatisticheServiziForm(request.POST or None, initial={"sedi": sedi})
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

            fine = oggi - timedelta(days=(giorni * periodo))
            inizio = fine - timedelta(days=giorni - 1)

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

            ore_di_servizio = qs_turni.annotate(durata=F('fine') - F('inizio')).aggregate(totale_ore=Sum('durata'))[
                                  'totale_ore'] or timedelta()
            ore_uomo_di_servizio = \
            qs_part.annotate(durata=F('turno__fine') - F('turno__inizio')).aggregate(totale_ore=Sum('durata'))[
                'totale_ore'] or timedelta()

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


@pagina_privata
def so_mezzi(request, me):
    mie_sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not mie_sedi:
        messages.error(request, 'Non hai sedi SO da gestire.')
        return redirect(reverse('so:index'))

    form = CreazioneMezzoSO(request.POST or None)
    form.fields['estensione'].queryset = mie_sedi

    if request.method == 'POST':
        if form.is_valid():
            mezzo = form.save(commit=False)
            mezzo.creato_da = me
            mezzo.save()

            messages.success(request, 'Il %s è stato creato con successo.' % mezzo.get_tipo_display())
            return redirect('so:mezzi')

    mezzi_materiali = MezzoSO.disponibili_per_sedi(mie_sedi)

    context = {
        'mezzi': mezzi_materiali.filter(tipo=MezzoSO.MEZZO),
        'materiali': mezzi_materiali.filter(tipo=MezzoSO.MATERIALE),
        'form': form
    }
    return 'so_mezzi_e_materiali.html', context


@pagina_privata
def so_mezzo_cancella(request, me, pk):
    mm = get_object_or_404(MezzoSO, pk=pk)

    mie_sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if mm.estensione not in mie_sedi:
        return redirect(ERRORE_PERMESSI)

    mm.delete()
    messages.success(request, 'Il mezzo/materiale selezionato è stato rimosso.')
    return redirect(reverse('so:mezzi'))


@pagina_privata
def so_mezzo_modifica(request, me, pk):
    mezzo = get_object_or_404(MezzoSO, pk=pk)
    mie_sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)

    if mezzo.estensione not in mie_sedi:
        return redirect(ERRORE_PERMESSI)

    if mezzo.creato_da != me:
        return redirect(ERRORE_PERMESSI)

    form = CreazioneMezzoSO(request.POST or None, instance=mezzo)
    form.fields['estensione'].queryset = mie_sedi

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('so:mezzi'))

    context = {
        'form': form,
        'mezzo': mezzo,
    }
    return 'so_mezzi_e_materiali_edit.html', context


@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_scheda_conferma(request, me, pk):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    servizio.conferma_servizio()

    return redirect(reverse('so:servizio_modifica', args=[pk, ]))


@pagina_privata(permessi=(GESTIONE_SERVIZI,))
def so_scheda_richiedi_conferma(request, me, pk):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    servizio.richiede_approvazione(me)

    return redirect(reverse('so:servizio_modifica', args=[pk, ]))


@pagina_privata
def so_scheda_attestati(request, me, pk):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    puo_modificare = me.permessi_almeno(servizio, MODIFICA)

    partecipanti_confermati = servizio.partecipanti_confermati()
    partecipazioni = None

    if not puo_modificare:
        if not me in partecipanti_confermati:
            messages.error(request, 'Non hai accesso alla pagina attestati del Servizio.')
            return redirect(servizio.url)

    if me in partecipanti_confermati:
        partecipazioni = PartecipazioneSO.di_persona(
            turno__in=servizio.turni(),
            turno__fine__lt=now(),
        )

    context = {
        'attivita': servizio,
        'puo_modificare': puo_modificare,
        'partecipazioni': partecipazioni,
    }

    return 'so_scheda_scarica_attestato.html', context


@pagina_privata
def so_scheda_scarica_attestato(request, me, pk, partecipazione_pk):
    partecipazione = get_object_or_404(PartecipazioneSO, pk=partecipazione_pk)
    attestato = partecipazione.genera_attestato(request)

    with open(attestato.file.path, 'rb') as f:
        pdf = f.read()

    filename = 'Attestato-turno.pdf'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response.write(pdf)
    return response


@pagina_privata
def utente_datore_di_lavoro_modifica(request, me, pk=None):
    datore = get_object_or_404(DatoreLavoro, pk=pk)

    form = ModuloProfiloModificaAnagraficaDatoreLavoro(request.POST or None, instance=datore)

    if request.method == 'POST':
        if form.is_valid():
            datore = form.save(commit=False)
            datore.save()
            return redirect(reverse('so:datore_di_lavoro'))

    context = {
        'form': form,
        'datore': datore,
    }
    return 'so_utente_datore_lavoro_modifica.html', context

@pagina_privata
def utente_datore_di_lavoro(request, me):
    form = ModuloProfiloModificaAnagraficaDatoreLavoro(request.POST or None)

    if request.POST:
        if form.is_valid():
            datore = form.save(commit=False)
            datore.persona = me
            datore.save()

    context = {
        "form": form,
        "datori": DatoreLavoro.objects.filter(persona=me)
    }
    return 'so_utente_datore_lavoro.html', context


@pagina_privata
def utente_datore_di_lavoro_cancella(request, me, pk=None):
    datore = get_object_or_404(DatoreLavoro, pk=pk)

    datore.delete()
    messages.success(request, 'Il datore selezionato è stato rimosso.')
    return redirect(reverse('so:datore_di_lavoro'))


@pagina_privata
def so_organizza_operazione(request, me):

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not sedi:
        messages.error(request, 'Non hai sedi con la delega SO.')
        return redirect(reverse('so:index'))

    form_referente = OrganizzaOperazioneReferenteForm(request.POST or None)

    form = OrganizzaOperazioneForm(request.POST or None)
    form.fields['sede'].queryset = sedi

    if form.is_valid() and form_referente.is_valid():
        cd = form.cleaned_data
        form_referente_cd = form_referente.cleaned_data
        operazione = form.save(commit=False)
        operazione.save()

        for funzione in cd['funzioni']:
            operazione.funzioni.add(funzione)

        if cd['comitato'] == OperazioneSO.NAZIONALI:
            for sede in cd['sede']:
                operazione.sede.add(sede)
        elif cd['comitato'] == OperazioneSO.INTERNAZIONALE:
            for sede in cd['sede_internazionale']:
                operazione.sede_internazionale.add(sede)

        operazione.save()

        if form_referente_cd['scelta'] == form_referente.SONO_IO:
            # Io sono il referente.
            operazione.aggiungi_delegato(REFERENTE_OPERAZIONE_SO, me, firmatario=me, inizio=poco_fa())
            return redirect(operazione.url_modifica)

        elif form_referente_cd['scelta'] == form_referente.SCEGLI_REFERENTI:
            # Il referente è qualcun altro.
            return redirect(reverse('so:organizza_referenti_operazione', args=[operazione.pk, ]))

    context = {
        "modulo": form,
        "modulo_referente": form_referente,
    }
    return 'so_organizza_operazione.html', context


@pagina_privata
def so_gestisci_operazione(request, me, stato="aperte"):

    operazioni_tutti = me.oggetti_permesso(GESTIONE_OPERAZIONI, solo_deleghe_attive=False)

    operazioni_aperti = operazioni_tutti.filter(archivia_emergenza=False)
    operazioni_chiusi = operazioni_tutti.filter(archivia_emergenza=True)

    operazioni = operazioni_aperti if stato == "aperte" else operazioni_chiusi

    context = {
        "stato": stato,
        "operazioni_n": operazioni.filter(sede__estensione=NAZIONALE),
        "operazioni_l": operazioni.filter(sede__estensione=LOCALE),
        "operazioni_p": operazioni.filter(sede__estensione=PROVINCIALE),
        "operazioni_r": operazioni.filter(sede__estensione=REGIONALE),
        "operazioni_i": operazioni.filter(sede_internazionale__isnull=False),
        "operazioni_aperti": operazioni_aperti.count(),
        "operazioni_chiusi": operazioni_chiusi.count(),
        "servizio_referenti_modificabili": me.oggetti_permesso(GESTIONE_REFERENTI_OPERAZIONI_SO),
    }
    return 'so_gestisci_operazioni.html', context


@pagina_privata(permessi=(GESTIONE_OPERAZIONI,))
def so_scheda_informazioni_modifica_operazione(request, me, pk=None):
    operazione = get_object_or_404(OperazioneSO, pk=pk)

    if not me.permessi_almeno(operazione, MODIFICA):
        if me.permessi_almeno(operazione, MODIFICA, solo_deleghe_attive=False):
            # Se la mia delega e' sospesa per l'attivita', vai in prima pagina per riattivarla.
            return redirect(operazione.url)
        return redirect(ERRORE_PERMESSI)

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not sedi:
        messages.error(request, 'Non hai sedi con la delega SO.')
        return redirect(reverse('so:index'))

    form = OrganizzaOperazioneForm(request.POST or None, instance=operazione)
    form.fields['sede'].queryset = sedi

    if form.is_valid():
        form.save()

    context = {
        "me": me,
        "operazione": operazione,
        "puo_modificare": True,
        "modulo": form,
    }
    return 'so_scheda_informazioni_modifica_operazione.html', context


@pagina_pubblica
def so_scheda_informazioni_info_operazione(request, me=None, pk=None):
    operazione = get_object_or_404(OperazioneSO, pk=pk)
    puo_modificare = me and me.permessi_almeno(operazione, MODIFICA)

    context = {
        "operazione": operazione,
        "puo_modificare": puo_modificare,
        "me": me,
    }
    return 'so_scheda_operazione_informazioni.html', context


@pagina_privata
def so_scheda_cancella_operazione(request, me, pk):
    operazione = get_object_or_404(OperazioneSO, pk=pk)
    if not me and me.permessi_almeno(operazione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    titolo_messaggio = "Operazione cancellata"
    testo_messaggio = "L'operazione è stato cancellato con successo."

    operazione.delete()

    return messaggio_generico(request, me,
                              titolo=titolo_messaggio,
                              messaggio=testo_messaggio,
                              torna_titolo="Gestione operazione",
                              torna_url=reverse('so:gestisce_operazione'), )


@pagina_privata
def so_organizza_funzione(request, me):

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not sedi:
        messages.error(request, 'Non hai sedi con la delega SO.')
        return redirect(reverse('so:index'))

    form_referente = OrganizzaFunzioneReferenteForm(request.POST or None)

    form = OrganizzaFunzioneForm(request.POST or None)

    if form.is_valid() and form_referente.is_valid():
        cd = form.cleaned_data
        form_referente_cd = form_referente.cleaned_data

        funzione = form.save(commit=False)
        funzione.creato_da = me
        funzione.save()

        if form_referente_cd['scelta'] == form_referente.SONO_IO:
            # Io sono il referente.
            funzione.aggiungi_delegato(REFERENTE_FUNZIONE_SO, me, firmatario=me, inizio=poco_fa())
            return redirect(funzione.url_gestione)

        elif form_referente_cd['scelta'] == form_referente.SCEGLI_REFERENTI:
            # Il referente è qualcun altro.
            return redirect(reverse('so:organizza_referenti_funzione', args=[funzione.pk, ]))

    context = {
        "modulo": form,
        "modulo_referente": form_referente,
    }
    return 'so_organizza_funzione.html', context


@pagina_privata
def so_referenti_funzione(request, me, pk=None, nuova=False):
    funzione = get_object_or_404(FunzioneSO, pk=pk)

    if not me.permessi_almeno(funzione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    delega = REFERENTE_FUNZIONE_SO

    if nuova:
        continua_url = reverse('so:organizza_funzione_fatto', args=[funzione.pk,])
    else:
        continua_url = reverse('so:gestisce_funzione')

    context = {
        "delega": delega,
        "servizio": funzione,
        "continua_url": continua_url
    }
    return 'so_referenti.html', context


@pagina_privata
def so_organizza_funzione_fatto(request, me, pk=None):
    funzione = get_object_or_404(FunzioneSO, pk=pk)
    if not me.permessi_almeno(funzione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    return messaggio_generico(request, me,
        titolo="Operazione organizzato",
        messaggio="Abbiamo inviato un messaggio ai referenti che hai selezionato. "
                  "Appena accederanno a Gaia, gli chiederemo di darci maggiori informazioni sulla funzione, "
                  "come gli orari dei turni e l'indirizzo.",
        torna_titolo="Torna a Organizza funzione",
        torna_url=reverse('so:gestisce_funzione'))



@pagina_privata
def so_gestisci_funzione(request, me):
    creati_da = []

    for sede in me.oggetti_permesso(GESTIONE_SO_SEDE, solo_deleghe_attive=False):
        creati_da.append(sede.presidente())
        creati_da.extend(list(sede.commissari()))
        creati_da.extend(list(sede.commissari()))
        creati_da.extend(list(sede.obbiettivo_3()))
        creati_da.extend(list(sede.delegati_so()))

    context = {
        "funzioni": FunzioneSO.objects.filter(creato_da__in=creati_da),
    }
    return 'so_gestisci_funzioni.html', context


@pagina_privata(permessi=(GESTIONE_FUNZIONI,))
def so_scheda_informazioni_modifica_funzione(request, me, pk=None):
    funzione = get_object_or_404(FunzioneSO, pk=pk)

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
    if not sedi:
        messages.error(request, 'Non hai sedi con la delega SO.')
        return redirect(reverse('so:index'))

    form = OrganizzaFunzioneForm(request.POST or None, instance=funzione)

    if form.is_valid():
        form.save()
        return redirect(reverse('so:gestisce_funzione'))

    context = {
        "me": me,
        "funzione": funzione,
        "puo_modificare": True,
        "modulo": form,
    }
    return 'so_modifica_funzione.html', context


@pagina_privata
def so_scheda_cancella_funzione(request, me, pk):
    funzione = get_object_or_404(FunzioneSO, pk=pk)
    if not me and me.permessi_almeno(funzione, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    titolo_messaggio = "Funzione cancellata"
    testo_messaggio = "La funzione è stato cancellato con successo."

    funzione.delete()

    return messaggio_generico(request, me,
                              titolo=titolo_messaggio,
                              messaggio=testo_messaggio,
                              torna_titolo="Organizza funzioni",
                              torna_url=reverse('so:gestisce_funzione'), )


@pagina_privata
def so_scheda_chiudi(request, me, pk):

    servizio = get_object_or_404(ServizioSO, pk=pk)

    titolo_messaggio = "Servizio chiudi"
    testo_messaggio = "Il Servizio è stato chiuso con successo."

    servizio.apertura = ServizioSO.CHIUSA

    servizio.save()

    return messaggio_generico(request, me,
                              titolo=titolo_messaggio,
                              messaggio=testo_messaggio,
                              torna_titolo="Gestione servizio",
                              torna_url=reverse('so:gestisci'), )
