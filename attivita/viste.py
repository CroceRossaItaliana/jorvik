# coding=utf8
import json
from datetime import date, timedelta, datetime, time

from django.db.models import Count, F, Sum
from django.utils import timezone


from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404

from anagrafica.costanti import NAZIONALE
from anagrafica.models import Sede
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA, DELEGATO_AREA, REFERENTE
from anagrafica.permessi.costanti import MODIFICA, GESTIONE_ATTIVITA, ERRORE_PERMESSI, GESTIONE_GRUPPO, \
    GESTIONE_AREE_SEDE, COMPLETO, GESTIONE_ATTIVITA_AREA, GESTIONE_REFERENTI_ATTIVITA, GESTIONE_ATTIVITA_SEDE, \
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE
from attivita.elenchi import ElencoPartecipantiTurno, ElencoPartecipantiAttivita
from attivita.forms import ModuloStoricoTurni, ModuloAttivitaInformazioni, ModuloModificaTurno, \
    ModuloAggiungiPartecipanti, ModuloCreazioneTurno, ModuloCreazioneArea, ModuloOrganizzaAttivita, \
    ModuloOrganizzaAttivitaReferente, ModuloStatisticheAttivita, ModuloRipetiTurno
from attivita.models import Partecipazione, Attivita, Turno, Area
from attivita.utils import turni_raggruppa_giorno
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import ci_siamo_quasi, errore_generico, messaggio_generico
from base.files import Excel, FoglioExcel
from base.utils import poco_fa, timedelta_ore
from gruppi.models import Gruppo


def attivita(request):
    return redirect('/attivita/calendario/')


@pagina_privata
def attivita_aree(request, me):
    sedi = me.oggetti_permesso(GESTIONE_AREE_SEDE)
    contesto = {
        "sedi": sedi,
    }
    return 'attivita_aree.html', contesto


@pagina_privata
def attivita_aree_sede(request, me, sede_pk=None):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not sede in me.oggetti_permesso(GESTIONE_AREE_SEDE):
        return redirect(ERRORE_PERMESSI)
    aree = sede.aree.all()
    modulo = ModuloCreazioneArea(request.POST or None)
    if modulo.is_valid():
        area = modulo.save(commit=False)
        area.sede = sede
        area.save()
        return redirect("/attivita/aree/%d/%d/responsabili/" % (
            sede.pk, area.pk,
        ))
    contesto = {
        "sede": sede,
        "aree": aree,
        "modulo": modulo,
    }
    return 'attivita_aree_sede.html', contesto


@pagina_privata
def attivita_aree_sede_area_responsabili(request, me, sede_pk=None, area_pk=None):
    area = get_object_or_404(Area, pk=area_pk)
    if not me.permessi_almeno(area, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    sede = area.sede
    delega = DELEGATO_AREA
    contesto = {
        "area": area,
        "delega": delega,
        "continua_url": "/attivita/aree/%d/" % (sede.pk,)
    }
    return 'attivita_aree_sede_area_responsabili.html', contesto


@pagina_privata
def attivita_aree_sede_area_cancella(request, me, sede_pk=None, area_pk=None):
    area = get_object_or_404(Area, pk=area_pk)
    if not me.permessi_almeno(area, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    sede = area.sede
    if area.attivita.exists():
        return errore_generico(request, me, titolo="L'area ha delle attività associate",
                               messaggio="Non è possibile cancellare delle aree che hanno delle "
                                         "attività associate.",
                               torna_titolo="Torna indietro",
                               torna_url="/attivita/aree/%d/" % (sede.pk,))
    area.delete()
    return redirect("/attivita/aree/%d/" % (sede.pk,))


@pagina_privata
def attivita_gestisci(request, me, stato="aperte"):
    # stato = "aperte" | "chiuse"

    attivita_tutte = me.oggetti_permesso(GESTIONE_ATTIVITA)
    attivita_aperte = attivita_tutte.filter(apertura=Attivita.APERTA)
    attivita_chiuse = attivita_tutte.filter(apertura=Attivita.CHIUSA)

    if stato == "aperte":
        attivita = attivita_aperte
    else:  # stato == "chiuse"
        attivita = attivita_chiuse

    attivita_referenti_modificabili = me.oggetti_permesso(GESTIONE_REFERENTI_ATTIVITA)

    attivita = attivita.annotate(num_turni=Count('turni'))
    contesto = {
        "stato": stato,
        "attivita": attivita,
        "attivita_aperte": attivita_aperte,
        "attivita_chiuse": attivita_chiuse,
        "attivita_referenti_modificabili": attivita_referenti_modificabili,
    }
    return 'attivita_gestisci.html', contesto


@pagina_privata
def attivita_organizza(request, me):
    aree = me.oggetti_permesso(GESTIONE_ATTIVITA_AREA)
    sedi = Sede.objects.filter(aree__in=aree)
    if not aree:
        return messaggio_generico(request, me, titolo="Crea un'area di intervento, prima!",
                                  messaggio="Le aree di intervento fungono da 'contenitori' per le "
                                            "attività. Per organizzare un'attività, è necessario creare "
                                            "almeno un'area di intervento. ",
                                  torna_titolo="Gestisci le Aree di intervento",
                                  torna_url="/attivita/aree/")
    modulo_referente = ModuloOrganizzaAttivitaReferente(request.POST or None)
    modulo = ModuloOrganizzaAttivita(request.POST or None)
    modulo.fields['area'].queryset = aree
    if modulo_referente.is_valid() and modulo.is_valid():
        attivita = modulo.save(commit=False)
        attivita.sede = attivita.area.sede
        attivita.estensione = attivita.sede.comitato
        attivita.save()

        if modulo_referente.cleaned_data['scelta'] == modulo_referente.SONO_IO:
            # Io sono il referente.
            attivita.aggiungi_delegato(REFERENTE, me, firmatario=me, inizio=poco_fa())
            return redirect(attivita.url_modifica)

        else:  # Il referente e' qualcun altro.
            return redirect("/attivita/organizza/%d/referenti/" % (attivita.pk,))

    contesto = {
        "modulo": modulo,
        "modulo_referente": modulo_referente,
    }
    return 'attivita_organizza.html', contesto


@pagina_privata
def attivita_organizza_fatto(request, me, pk=None):
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    return messaggio_generico(request, me, titolo="Attività organizzata",
                              messaggio="Abbiamo inviato un messaggio ai referenti che hai "
                                        "selezionato. Appena accederanno a Gaia, gli chiederemo "
                                        "di darci maggiori informazioni sull'attività, come "
                                        "gli orari dei turni e l'indirizzo.",
                              torna_titolo="Torna a Gestione Attività",
                              torna_url="/attivita/gestisci/")


@pagina_privata
def attivita_referenti(request, me, pk=None, nuova=False):
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    delega = REFERENTE

    if nuova:
        continua_url = "/attivita/organizza/%d/fatto/" % (attivita.pk,)
    else:
        continua_url = "/attivita/gestisci/"

    contesto = {
        "delega": delega,
        "attivita": attivita,
        "continua_url": continua_url
    }
    return 'attivita_referenti.html', contesto



@pagina_privata
def attivita_calendario(request, me=None, inizio=None, fine=None, vista="calendario"):
    """
    Mostra il calendario delle attivita' personalizzato.
    """

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
        return attivita_calendario(request, me, inizio=inizio, fine=None)


    # Successivo
    successivo_inizio = inizio + differenza
    successivo_inizio_stringa = successivo_inizio.strftime(FORMATO)
    successivo_fine = fine + differenza
    successivo_fine_stringa = successivo_fine.strftime(FORMATO)

    successivo_url = "/attivita/calendario/%s/%s/" % (successivo_inizio_stringa, successivo_fine_stringa, )

    # Oggi
    oggi_url = "/attivita/calendario/"

    # Precedente
    precedente_inizio = inizio - differenza
    precedente_inizio_stringa = precedente_inizio.strftime(FORMATO)
    precedente_fine = fine - differenza
    precedente_fine_stringa = precedente_fine.strftime(FORMATO)

    precedente_url = "/attivita/calendario/%s/%s/" % (precedente_inizio_stringa, precedente_fine_stringa, )


    # Elenco
    turni = me.calendario_turni(inizio, fine)
    raggruppati = turni_raggruppa_giorno(turni)

    contesto = {
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

    return 'attivita_calendario.html', contesto

@pagina_privata
def attivita_storico(request, me):
    """
    Mostra uno storico delle attivita' a cui ho chiesto di partecipare/partecipato.
    """
    storico = Partecipazione.objects.filter(persona=me).order_by('-turno__inizio')

    contesto = {
        "storico": storico
    }

    return 'attivita_storico.html', contesto\

@pagina_privata
def attivita_storico_excel(request, me):
    """
    Scarica il foglio di servizio
    """
    excel = me.genera_foglio_di_servizio()
    return redirect(excel.download_url)


@pagina_pubblica
def attivita_scheda_informazioni(request, me=None, pk=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    attivita = get_object_or_404(Attivita, pk=pk)
    puo_modificare = me and me.permessi_almeno(attivita, MODIFICA)

    contesto = {
        "attivita": attivita,
        "puo_modificare": puo_modificare,
    }

    return 'attivita_scheda_informazioni.html', contesto


@pagina_privata
def attivita_scheda_cancella(request, me, pk):
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if not attivita.cancellabile:
        return errore_generico(request, me, titolo="Attività non cancellabile",
                               messaggio="Questa attività non può essere cancellata.")

    attivita.delete()
    return messaggio_generico(request, me, titolo="Attività cancellata",
                              messaggio="L'attività è stata cancellata con successo.",
                              torna_titolo="Gestione attività", torna_url="/attivita/gestisci/")


@pagina_pubblica
def attivita_scheda_mappa(request, me=None, pk=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    attivita = get_object_or_404(Attivita, pk=pk)
    puo_modificare = me and me.permessi_almeno(attivita, MODIFICA)
    contesto = {
        "attivita": attivita,
        "puo_modificare": puo_modificare,
    }

    return 'attivita_scheda_mappa.html', contesto

@pagina_privata
def attivita_scheda_turni(request, me=None, pk=None, pagina=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    if False:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(Attivita, pk=pk)

    if pagina is None:
        pagina = "/attivita/scheda/%d/turni/%d/" % (attivita.pk, attivita.pagina_turni_oggi())
        return redirect(pagina)

    turni = attivita.turni.all()

    puo_modificare = me and me.permessi_almeno(attivita, MODIFICA)

    evidenzia_turno = Turno.objects.get(pk=request.GET['evidenzia_turno']) if 'evidenzia_turno' in request.GET else None

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(turni, Turno.PER_PAGINA)
    pg = p.page(pagina)

    contesto = {
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
    return 'attivita_scheda_turni.html', contesto


@pagina_privata
def attivita_scheda_turni_nuovo(request, me=None, pk=None):
    """
    Pagina di creazione di un nuovo turno
    """

    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        redirect(ERRORE_PERMESSI)

    tra_una_settimana = timezone.now() + timedelta(days=7)
    tra_una_settimana_e_una_ora = tra_una_settimana + timedelta(hours=1)

    modulo = ModuloCreazioneTurno(request.POST or None, initial={
      "inizio": tra_una_settimana, "fine": tra_una_settimana_e_una_ora,
    })

    modulo_ripeti = ModuloRipetiTurno(request.POST or None, prefix="ripeti")

    if modulo.is_valid():
        turno = modulo.save(commit=False)
        turno.attivita = attivita
        turno.save()

        if request.POST.get('ripeti', default="no") == 'si' \
                and modulo_ripeti.is_valid():
            numero_ripetizioni = modulo_ripeti.cleaned_data['numero_ripetizioni']
            giorni = modulo_ripeti.cleaned_data['giorni']

            giorni_ripetuti = 0
            giorni_nel_futuro = 1
            while giorni_ripetuti < numero_ripetizioni:

                ripetizione = Turno(
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


    contesto = {
        "modulo": modulo,
        "modulo_ripeti": modulo_ripeti,
        "attivita": attivita,
        "puo_modificare": True
    }
    return 'attivita_scheda_turni_nuovo.html', contesto


@pagina_privata
def attivita_scheda_turni_turno_cancella(request, me, pk=None, turno_pk=None):
    turno = Turno.objects.get(pk=turno_pk)
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
def attivita_scheda_turni_partecipa(request, me, pk=None, turno_pk=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    turno = get_object_or_404(Turno, pk=turno_pk)
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

    p = Partecipazione(
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
def attivita_scheda_turni_ritirati(request, me, pk=None, turno_pk=None):

    turno = get_object_or_404(Turno, pk=turno_pk)
    stato = turno.persona(me)

    if stato != turno.TURNO_PRENOTATO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente dell'attività, che potrà valutare "
                                         "la situazione e rimuoverti dai partecipanti.",
                               torna_titolo="Torna al turno",
                               torna_url=turno.url)

    partecipazione = Partecipazione.con_esito_pending(turno=turno, persona=me).first()
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
def attivita_scheda_turni_partecipanti(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(Turno, pk=turno_pk)
    if not me.permessi_almeno(turno.attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    elenco = ElencoPartecipantiTurno(turno.queryset_modello())
    contesto = {
        "attivita": turno.attivita,
        "turno": turno,
        "elenco": elenco,
        "puo_modificare": True
    }
    return "attivita_scheda_turni_elenco.html", contesto


@pagina_privata
def attivita_scheda_partecipanti(request, me, pk=None):
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    elenco = ElencoPartecipantiAttivita(attivita.queryset_modello())
    contesto = {
        "attivita": attivita,
        "elenco": elenco,
        "puo_modificare": True
    }
    return "attivita_scheda_partecipanti.html", contesto



@pagina_privata
def attivita_scheda_turni_rimuovi(request, me, pk=None, turno_pk=None, partecipante_pk=None):

    turno = get_object_or_404(Turno, pk=turno_pk)
    stato = turno.persona(me)

    if stato != turno.TURNO_PRENOTATO_PUOI_RITIRARTI:
        return errore_generico(request, me, titolo="Non puoi ritirare la tua partecipazione",
                               messaggio="Una volta che la tua partecipazione è stata confermata, "
                                         "non puoi più ritirarla da Gaia. Se non puoi presentarti, "
                                         "scrivi a un referente dell'attività, che potrà valutare "
                                         "la situazione e rimuoverti dai partecipanti.",
                               torna_titolo="Torna al turno",
                               torna_url=turno.url)

    partecipazione = Partecipazione.con_esito_pending(turno=turno, persona=me).first()
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
def attivita_scheda_turni_link_permanente(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(Turno, pk=turno_pk)
    attivita = turno.attivita
    pagina = turno.elenco_pagina()

    return redirect("/attivita/scheda/%d/turni/%d/?evidenzia_turno=%d#turno-%d" % (
        attivita.pk, pagina, turno.pk, turno.pk,
    ))


@pagina_privata
def attivita_scheda_turni_modifica_link_permanente(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(Turno, pk=turno_pk)
    attivita = turno.attivita
    pagina = turno.elenco_pagina()

    return redirect("/attivita/scheda/%d/turni/modifica/%d/?evidenzia_turno=%d#turno-%d" % (
        attivita.pk, pagina, turno.pk, turno.pk
    ))



@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def attivita_scheda_informazioni_modifica(request, me, pk=None):
    """
    Mostra la pagina di modifica di una attivita'.
    """
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if not me.ha_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE):
        request.POST = request.POST.copy()
        request.POST['centrale_operativa'] = attivita.centrale_operativa

    modulo = ModuloAttivitaInformazioni(request.POST or None, instance=attivita)
    modulo.fields['estensione'].queryset = attivita.sede.get_ancestors(include_self=True).exclude(estensione=NAZIONALE)

    if not me.ha_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE):
        modulo.fields['centrale_operativa'].widget.attrs['disabled'] = True

    if modulo.is_valid():
        modulo.save()

    contesto = {
        "attivita": attivita,
        "puo_modificare": True,
        "modulo": modulo,
    }

    return 'attivita_scheda_informazioni_modifica.html', contesto

@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def attivita_scheda_turni_modifica(request, me, pk=None, pagina=None):
    """
    Mostra la pagina di modifica di una attivita'.
    """

    if False:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if pagina is None:
        pagina = "/attivita/scheda/%d/turni/modifica/%d/" % (attivita.pk, attivita.pagina_turni_oggi())
        return redirect(pagina)

    turni = attivita.turni.all()

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(turni, Turno.PER_PAGINA)
    pg = p.page(pagina)

    moduli = []
    moduli_aggiungi_partecipanti = []
    turni = pg.object_list
    for turno in turni:
        modulo = ModuloModificaTurno(request.POST or None,
                                     instance=turno,
                                     prefix="turno_%d" % (turno.pk,))
        moduli += [modulo]

        modulo_aggiungi_partecipanti = ModuloAggiungiPartecipanti(request.POST or None,
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
            pa = Partecipazione.objects.get(pk=p_pk)
            pa.stato = Partecipazione.RICHIESTA if p_si else Partecipazione.NON_PRESENTATO
            pa.save()

    turni_e_moduli = zip(turni, moduli, moduli_aggiungi_partecipanti)

    evidenzia_turno = Turno.objects.get(pk=request.GET['evidenzia_turno']) if 'evidenzia_turno' in request.GET else None

    contesto = {
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

    return 'attivita_scheda_turni_modifica.html', contesto


@pagina_privata
def attivita_scheda_partecipazione_cancella(request, me, pk, partecipazione_pk):
    partecipazione = get_object_or_404(Partecipazione, pk=partecipazione_pk)

    if not me.permessi_almeno(partecipazione.turno.attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    turno = partecipazione.turno
    partecipazione.delete()
    return redirect(turno.url_modifica)


@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def attivita_scheda_report(request, me, pk=None):
    """
    Mostra la pagina di modifica di una attivita'.
    """

    if False:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if request.POST:
        pdf = attivita.genera_report()
        return redirect(pdf.download_url)

    contesto = {
        "attivita": attivita,
        "puo_modificare": True,
    }

    return 'attivita_scheda_report.html', contesto


@pagina_privata
def attivita_statistiche(request, me):
    sedi = me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE)

    modulo = ModuloStatisticheAttivita(request.POST or None, initial={"sedi": sedi})
    modulo.fields['sedi'].queryset = sedi

    statistiche = []
    chart = {}

    periodi = 12

    if modulo.is_valid():

        oggi = date.today()

        giorni = int(modulo.cleaned_data['periodo'])
        if giorni == modulo.SETTIMANA:
            etichetta = "sett."
        elif giorni == modulo.QUINDICI_GIORNI:
            etichetta = "fortn."
        elif giorni == modulo.MESE:
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
            qs_attivita = Attivita.objects.filter(stato=Attivita.VISIBILE, sede__in=sedi)
            qs_turni = Turno.objects.filter(attivita__in=qs_attivita, inizio__lte=fine, fine__gte=inizio)
            qs_part = Partecipazione.con_esito_ok(turno__in=qs_turni)

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

    contesto = {
        "modulo": modulo,
        "statistiche": statistiche,
        "chart": chart,
    }
    return 'attivita_statistiche.html', contesto
