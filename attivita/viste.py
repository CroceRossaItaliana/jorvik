from datetime import date, timedelta, datetime
from django.shortcuts import redirect, get_object_or_404
from attivita.forms import ModuloStoricoTurni
from attivita.models import Partecipazione, Attivita
from attivita.utils import turni_raggruppa_giorno
from autenticazione.funzioni import pagina_privata, pagina_pubblica


def attivita(request):
    return redirect('/attivita/calendario/')

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
    print(raggruppati)

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
    storico = Partecipazione.objects.filter(persona=me).order_by('-creazione')
    form = None

    anni = Partecipazione.confermate().filter(persona=me).\
        dates('turno__inizio', 'year', order='DESC')

    if anni:
        form = ModuloStoricoTurni(anni)

    contesto = {
        "form": form,
        "storico": storico
    }

    return 'attivita_storico.html', contesto

@pagina_privata
def attivita_gruppi(request, me):
    """
    Mostra i gruppi di cui faccio parte, assieme ai controlli necessari a iscriversi a nuovi gruppi.
    """

    return 'attivita_vuota.html'

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
    contesto = {
        "attivita": attivita
    }

    return 'attivita_scheda_informazioni.html', contesto

@pagina_pubblica
def attivita_scheda_mappa(request, me=None, pk=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    attivita = get_object_or_404(Attivita, pk=pk)
    contesto = {
        "attivita": attivita
    }

    return 'attivita_scheda_informazioni.html', contesto

@pagina_privata
def attivita_scheda_turni(request, me=None, pk=None, turno=None):
    """
    Mostra la scheda "Informazioni" di una attivita'.
    """

    attivita = get_object_or_404(Attivita, pk=pk)
    contesto = {
        "attivita": attivita
    }

    return 'attivita_scheda_informazioni.html', contesto