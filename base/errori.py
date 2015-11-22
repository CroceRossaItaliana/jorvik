from anagrafica.models import Persona
from autenticazione.funzioni import pagina_pubblica

__author__ = 'alfioemanuele'

"""
Qui sono contenute le varie viste relative agli errori (namespace /errore/*)
"""

@pagina_pubblica
def non_trovato(request, me):
    """
    Questa vista viene chiamata quando una pagina non viene trovata (404) o un oggetto in una ricerca.
    :param request:
    :return:
    """
    return 'base_errore_404.html'

@pagina_pubblica
def orfano(request, me):
    """
    Questa vista viene chiamata quando un utente non ha una persona assegnata (utente "orfano").
    :param request:
    :return:
    """
    # Se il primo utente, istruisco sul come creare il resto...
    contesto = {
        "primo_utente": Persona.objects.all().count() == 0
    }
    return 'base_errore_orfano.html', contesto

@pagina_pubblica
def permessi(request, me):
    """
    Questa vista viene chiamata quando un utente tenta ad accedere a dei contenuti fuori competenza.
    :param request:
    :return:
    """
    return 'base_errore_permessi.html'

def errore_generico(request, me=None,
             titolo="Errore", messaggio="Si è verificato un errore generico.",
             torna_titolo="Home page", torna_url="/"):
    """
    Ritorna un errore generico con un link per tornare indietro.
    :param titolo: Il titolo del messaggio di errore.
    :param messaggio: Il messaggio di errore.
    :param torna_titolo: Il titolo del link per tornare alla pagina precedente.
    :param torna_url: L'URL della pagina precedente alla quale tornare.
    """
    contesto = {
        "errore_titolo": titolo,
        "errore_messaggio": messaggio,
        "errore_torna_titolo": torna_titolo,
        "errore_torna_url": torna_url,
    }
    return 'base_errore_generico.html', contesto
