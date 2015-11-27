from anagrafica.models import Appartenenza
from anagrafica.permessi.costanti import GESTIONE_SOCI
from autenticazione.funzioni import pagina_privata


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us(request, me):
    """
    Ritorna la home page per la gestione dei soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()

    contesto = {
        "sedi": sedi,
    }

    return 'us.html', contesto