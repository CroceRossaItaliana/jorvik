from django.shortcuts import redirect
from autenticazione.funzioni import pagina_privata

def attivita(request):
    return redirect('/attivita/calendario/')

@pagina_privata
def attivita_calendario(request, me):
    """
    Mostra il calendario delle attivita' personalizzato.
    """

    return 'attivita_vuota.html'

@pagina_privata
def attivita_storico(request, me):
    """
    Mostra uno storico delle attivita' a cui ho chiesto di partecipare/partecipato.
    """

    return 'attivita_vuota.html'

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