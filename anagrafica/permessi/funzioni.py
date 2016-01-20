"""
Questo modulo contiene tutte le funzioni per testare i permessi
a partire da un oggetto sul quale ho una delega ed un oggetto da testare.
"""
from anagrafica.permessi.applicazioni import PRESIDENTE, DIRETTORE_CORSO, RESPONSABILE_AUTOPARCO, REFERENTE_GRUPPO, \
    UFFICIO_SOCI_UNITA
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.applicazioni import DELEGATO_AREA
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA
from anagrafica.permessi.applicazioni import REFERENTE

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO, GESTIONE_AUTOPARCHI_SEDE, \
    GESTIONE_GRUPPI_SEDE, GESTIONE_GRUPPO


def permessi_presidente(sede):
    """
    Permessi della delega di PRESIDENTE.

    :param sede: Il sede di cui si e' presidenti.
    :return: Lista di permessi
    """

    sede_espansa = sede.espandi(includi_me=True)
    return [
        (GESTIONE_SEDE,         sede_espansa),
        (GESTIONE_GRUPPI_SEDE,  sede_espansa),
    ] \
        + permessi_ufficio_soci(sede) \
        + permessi_responsabile_attivita(sede) \
        + permessi_responsabile_formazione(sede) \
        + permessi_responsabile_autoparco(sede)


def permessi_ufficio_soci_unita(sede):
    """
    Permessi della delega di UFFICIO SOCI.

    :param sede: Sede di cui si e' ufficio soci.
    :return: Lista di permessi.
    """
    sede_qs = sede.queryset_modello()
    return [
        (GESTIONE_SOCI,     sede_qs),
        (ELENCHI_SOCI,      sede_qs),
    ]


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
    from attivita.models import Area, Attivita
    from gruppi.models import Gruppo
    sede_espansa = sede.espandi(includi_me=True)
    return [
        (GESTIONE_ATTIVITA_SEDE,    sede_espansa),
        (GESTIONE_ATTIVITA_AREA,    Area.objects.filter(sede__in=sede_espansa)),
        (GESTIONE_ATTIVITA,         Attivita.objects.filter(sede__in=sede_espansa)),
        (GESTIONE_GRUPPI_SEDE,      sede_espansa),
        (GESTIONE_GRUPPO,           Gruppo.objects.filter(sede__in=sede_espansa))
    ]


def permessi_referente_gruppo(gruppo):
    """
    Permessi della delega di REFERENTE DI GRUPPO.

    :param gruppo: Gruppo di cui si e' referenti.
    :return: Lista di permessi.
    """
    from gruppi.models import Gruppo
    return [
        (GESTIONE_GRUPPO,           Gruppo.objects.filter(pk=gruppo.pk))
    ]


def permessi_responsabile_formazione(sede):
    """
    Permessi della delega di RESPONSABILE DELLA FORMAZIONE.

    :param sede: Sede di cui si e' responsabile formazione.
    :return: Lista di permessi.
    """
    from anagrafica.models import Sede
    from formazione.models import CorsoBase
    sede_espansa = sede.espandi(includi_me=True)
    return [
        (GESTIONE_CORSI_SEDE,       sede_espansa),
        (GESTIONE_CORSO,            CorsoBase.objects.filter(sede__in=sede_espansa))

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


def permessi_responsabile_autoparco(sede):
    """
    Permessi della delega di RESPONSABILE AUTOPARCO.

    :param sede: La Sede di cui si gestiscono gli autoparchi
    :return: Lista di permessi.
    """
    return [
        (GESTIONE_AUTOPARCHI_SEDE,         sede.espandi(includi_me=True)),
    ]


# Non modificare


# Funzioni permessi
# Nota bene: Non inserire () dopo il nome della funzione.
PERMESSI_FUNZIONI = (
    (PRESIDENTE,                permessi_presidente),
    (UFFICIO_SOCI,              permessi_ufficio_soci),
    (UFFICIO_SOCI_UNITA,        permessi_ufficio_soci_unita),
    (DELEGATO_AREA,             permessi_delegato_area),
    (RESPONSABILE_AREA,         permessi_responsabile_area),
    (REFERENTE,                 permessi_referente),
    (DIRETTORE_CORSO,           permessi_direttore_corso),
    (RESPONSABILE_AUTOPARCO,    permessi_responsabile_autoparco),
    (REFERENTE_GRUPPO,          permessi_referente_gruppo),
)

# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_FUNZIONI_DICT = dict(PERMESSI_FUNZIONI)