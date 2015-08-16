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
    return 'base_errore_orfano.html'

@pagina_pubblica
def permessi(request, me):
    """
    Questa vista viene chiamata quando un utente tenta ad accedere a dei contenuti fuori competenza.
    :param request:
    :return:
    """
    return 'base_errore_permessi.html'
