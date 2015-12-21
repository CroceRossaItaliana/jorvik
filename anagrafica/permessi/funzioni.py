"""
Questo modulo contiene tutte le funzioni per testare i permessi
a partire da un oggetto sul quale ho una delega ed un oggetto da testare.
"""
from anagrafica.permessi.applicazioni import PRESIDENTE, DIRETTORE_CORSO
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.applicazioni import DELEGATO_AREA
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA
from anagrafica.permessi.applicazioni import REFERENTE

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO



def permessi_presidente(sede):
    """
    Permessi della delega di PRESIDENTE.

    :param sede: Il sede di cui si e' presidenti.
    :return: Lista di permessi
    """

    return [
       (GESTIONE_SEDE,      sede.espandi())
    ] \
        + permessi_ufficio_soci(sede) \
        + permessi_responsabile_attivita(sede) \
        + permessi_responsabile_formazione(sede)

def permessi_ufficio_soci(sede):
    """
    Permessi della delega di UFFICIO SOCI.

    :param sede: Sede di cui si e' ufficio soci.
    :return: Lista di permessi.
    """
    return [
        (GESTIONE_SOCI,     sede.espandi(includi_me=True)),
        (ELENCHI_SOCI,      sede.espandi(includi_me=True, pubblici=True)),
    ]

def permessi_responsabile_attivita(sede):
    """
    Permessi della delega di RESPONSABILE DELLE ATTIVITA'.

    :param sede: Sede di cui si e' responsabile attivita'.
    :return: Lista di permessi.
    """
    from anagrafica.models import Sede
    from attivita.models import Area, Attivita
    return [
        (GESTIONE_ATTIVITA_SEDE,    sede.espandi()),
        (GESTIONE_ATTIVITA_AREA,    Area.objects.filter(sede__in=sede.espandi())),
        (GESTIONE_ATTIVITA,         Attivita.objects.filter(sede__in=sede.espandi()))
    ]

def permessi_responsabile_formazione(sede):
    """
    Permessi della delega di RESPONSABILE DELLA FORMAZIONE.

    :param sede: Sede di cui si e' responsabile formazione.
    :return: Lista di permessi.
    """
    from anagrafica.models import Sede
    from formazione.models import CorsoBase
    return [
        (GESTIONE_CORSI_SEDE,       sede.espandi(includi_me=True)),
        (GESTIONE_CORSO,            CorsoBase.objects.filter(sede__in=sede.espandi(includi_me=True)))

    ]

def permessi_delegato_area(area):
    """
    Permessi della delega di DELEGATO D'AREA.

    :param area: L'area di cui si e' delegati
    :return: Lista di permessi.
    """
    from attivita.models import Area, Attivita
    return [
        (GESTIONE_ATTIVITA_AREA,    Area.objects.filter(pk=area.pk)),
        (GESTIONE_ATTIVITA,         Attivita.objects.filter(area=area))
    ]


def permessi_responsabile_area(area):
    """
    Permessi della delega di RESPONSABILE D'AREA.

    :param area: L'area di cui si e' responsabili
    :return: Lista di permessi.
    """
    return [
    ] \
        + permessi_delegato_area(area)


def permessi_referente(attivita):
    """
    Permessi della delega di REFERENTE ATTIVITA'.

    :param attivita: L'attivita' di cui si e' referenti
    :return: Lista di permessi.
    """
    from attivita.models import Attivita
    return [
        (GESTIONE_ATTIVITA,         Attivita.objects.filter(pk=attivita.pk))
    ]


def permessi_direttore_corso(corso):
    """
    Permessi della delega di DIRETTORE CORSO.

    :param corso: Il Corso di cui si e' referenti
    :return: Lista di permessi.
    """
    from formazione.models import CorsoBase
    return [
        (GESTIONE_CORSO,         CorsoBase.objects.filter(pk=corso.pk))
    ]


# Non modificare


# Funzioni permessi
# Nota bene: Non inserire () dopo il nome della funzione.
PERMESSI_FUNZIONI = (
    (PRESIDENTE,        permessi_presidente),
    (UFFICIO_SOCI,      permessi_ufficio_soci),
    (DELEGATO_AREA,     permessi_delegato_area),
    (RESPONSABILE_AREA, permessi_responsabile_area),
    (REFERENTE,         permessi_referente),
    (DIRETTORE_CORSO,   permessi_direttore_corso),
)

# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_FUNZIONI_DICT = dict(PERMESSI_FUNZIONI)