# coding=utf8

from datetime import date, timedelta, datetime

from django.db.models import Count
from django.utils import timezone


from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404

from anagrafica.costanti import NAZIONALE
from anagrafica.models import Sede
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA, DELEGATO_AREA, REFERENTE
from anagrafica.permessi.costanti import MODIFICA, GESTIONE_ATTIVITA, ERRORE_PERMESSI, GESTIONE_GRUPPO, \
    GESTIONE_AREE_SEDE, COMPLETO, GESTIONE_ATTIVITA_AREA, GESTIONE_REFERENTI_ATTIVITA
from attivita.forms import ModuloStoricoTurni, ModuloAttivitaInformazioni, ModuloModificaTurno, \
    ModuloAggiungiPartecipanti, ModuloCreazioneTurno, ModuloCreazioneArea, ModuloOrganizzaAttivita, \
    ModuloOrganizzaAttivitaReferente
from attivita.models import Partecipazione, Attivita, Turno, Area
from attivita.utils import turni_raggruppa_giorno
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import ci_siamo_quasi, errore_generico, messaggio_generico
from base.files import Excel, FoglioExcel
from base.utils import poco_fa
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

    storico = Partecipazione.confermate().filter(persona=me, stato=Partecipazione.RICHIESTA).order_by('-turno__inizio')

    anni = storico.dates('turno__inizio', 'year', order='DESC')

    excel = Excel(oggetto=me)

    # Per ogni anno, crea un foglio
    for anno in anni:

        anno = anno.year

        # Crea il nuovo foglio di lavoro
        foglio = FoglioExcel(
            nome="Anno %d" % (anno,),
            intestazione=(
                "Attivita", "Localita", "Turno", "Inizio", "Fine",
            )
        )

        # Aggiungi le partecipazioni
        for part in storico.filter(turno__inizio__year=anno):
            foglio.aggiungi_riga(
                part.turno.attivita.nome,
                part.turno.attivita.locazione if part.turno.attivita.locazione else 'N/A',
                part.turno.nome,
                part.turno.inizio,
                part.turno.fine,
            )

        excel.aggiungi_foglio(foglio)

    # Salva file excel e scarica
    excel.genera_e_salva("Foglio di servizio.xlsx")
    return redirect(excel.download_url)


@pagina_privata
def attivita_reperibilita(request, me):
    """
    Mostra uno storico delle reperibilita' segnalate, assieme ai controlli necessari per segnalarne di nuove.
    """

    return 'attivita_vuota.html'

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

    }
    return 'attivita_scheda_turni.html', contesto


@pagina_privata
def attivita_scheda_turni_nuovo(request, me=None, pk=None):
    """
    Pagina di creazione di un nuovo turno
    """

    if False:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        redirect(ERRORE_PERMESSI)

    tra_una_settimana = timezone.now() + timedelta(days=7)
    tra_una_settimana_e_una_ora = tra_una_settimana + timedelta(hours=1)

    modulo = ModuloCreazioneTurno(request.POST or None, initial={
      "inizio": tra_una_settimana, "fine": tra_una_settimana_e_una_ora,
    })

    if modulo.is_valid():
        turno = modulo.save(commit=False)
        turno.attivita = attivita
        turno.save()
        return redirect(turno.url)

    contesto = {
        "modulo": modulo,
        "attivita": attivita,
        "puo_modificare": True
    }
    return 'attivita_scheda_turni_nuovo.html', contesto


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

    return redirect("/attivita/scheda/%d/turni/%d/#%d" % (attivita.pk, pagina, turno.pk,))


@pagina_privata
def attivita_scheda_turni_modifica_link_permanente(request, me, pk=None, turno_pk=None):
    turno = get_object_or_404(Turno, pk=turno_pk)
    attivita = turno.attivita
    pagina = turno.elenco_pagina()

    return redirect("/attivita/scheda/%d/turni/modifica/%d/#%d" % (attivita.pk, pagina, turno.pk))



@pagina_privata(permessi=(GESTIONE_ATTIVITA,))
def attivita_scheda_informazioni_modifica(request, me, pk=None):
    """
    Mostra la pagina di modifica di una attivita'.
    """
    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    modulo = ModuloAttivitaInformazioni(request.POST or None, instance=attivita)
    modulo.fields['estensione'].queryset = attivita.sede.get_ancestors(include_self=True).exclude(estensione=NAZIONALE)
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

    if True:
        return ci_siamo_quasi(request, me)

    attivita = get_object_or_404(Attivita, pk=pk)
    if not me.permessi_almeno(attivita, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    contesto = {
        "attivita": attivita,
        "puo_modificare": True,
    }

    return 'attivita_scheda_report.html', contesto

