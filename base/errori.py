from anagrafica.models import Persona
from autenticazione.funzioni import pagina_pubblica

__author__ = 'alfioemanuele'

"""
Qui sono contenute le varie viste relative agli errori (namespace /errore/*)
"""

@pagina_pubblica
def non_trovato(request, me, exception=None):
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
             torna_titolo="Home page", torna_url="/", embed=False):
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
        "embed": embed,
    }
    return 'base_errore_generico.html', contesto


def messaggio_generico(request, me=None,
             titolo="OK", messaggio="Azione effettuata.",
             torna_titolo="Home page", torna_url="/", embed=False):
    """
    Ritorna un messaggio generico con un link per tornare indietro.
    :param titolo: Il titolo del messaggio .
    :param messaggio: Il messaggio .
    :param torna_titolo: Il titolo del link per tornare alla pagina precedente.
    :param torna_url: L'URL della pagina precedente alla quale tornare.
    """
    contesto = {
        "messaggio_titolo": titolo,
        "messaggio_messaggio": messaggio,
        "messaggio_torna_titolo": torna_titolo,
        "messaggio_torna_url": torna_url,
        "embed": embed
    }
    return 'base_messaggio_generico.html', contesto


def errore_nessuna_appartenenza(request, me=None, torna_url="/utente/"):
    return errore_generico(request, me,
                            titolo="Necessaria appartenenza,",
                            messaggio="Per effettuare questa azione è necessaria "
                                      "la verifica di un Presidente o delegato Ufficio Soci. "
                                      "Non hai alcuna appartenenza a una Sede CRI confermata su Gaia.",
                            torna_titolo="Torna indietro",
                            torna_url=torna_url,
                           )

def errore_no_volontario(request, me=None, torna_url="/utente/"):
    return errore_generico(request, me,
                            titolo="Accesso Volontari",
                            messaggio="Questa azione è disponibile ai soli volontari CRI.",
                            torna_titolo="Torna indietro",
                            torna_url=torna_url,
                           )


def ci_siamo_quasi(request, me):
    return messaggio_generico(request, me, titolo="Questa funzionalità sarà disponibile a breve",
                              messaggio="Stiamo perfezionando l'attivazione dei nuovi servizi di Gaia. "
                                        "Questa funzionalità non è ancora attiva, ma niente paura, non ci vorrà molto. "
                                        "Grazie per la pazienza -- Ti preghiamo di considerare che date "
                                        "le imminenti elezioni, stiamo dando priorità alle funzioni relative alla "
                                        "gestione dei soci e dell'elettorato.",
                              torna_titolo="Home page", torna_url="/")


@pagina_pubblica
def vista_ci_siamo_quasi(request, me):
    return ci_siamo_quasi(request, me)

