from anagrafica.models import Appartenenza, Persona
from anagrafica.permessi.costanti import GESTIONE_SOCI
from autenticazione.funzioni import pagina_privata
from ufficio_soci.forms import ModuloCreazioneEstensione


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


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensione(request, me):
    """
    Vista per la creazione di una nuova estensione da ufficio soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()  # es. per controllare che il volontario sia appartente attualmente
                                                         #     ad una delle sedi che gestisco io

    modulo = ModuloCreazioneEstensione(request.POST or None)

    # qui dovrebbe salvare...

    contesto = {
        "sedi": sedi,
        "modulo": modulo,
    }

    return 'us_estensione.html', contesto