"""
Questo modulo contiene tutte le funzioni per testare i permessi
a partire da un oggetto sul quale ho una delega ed un oggetto da testare.
"""
from datetime import timedelta

from django.db.models import QuerySet, Q

from anagrafica.permessi.applicazioni import PRESIDENTE, DIRETTORE_CORSO, RESPONSABILE_AUTOPARCO, REFERENTE_GRUPPO, \
    UFFICIO_SOCI_UNITA, DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, \
    DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, RESPONSABILE_FORMAZIONE, DELEGATO_CO
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.applicazioni import DELEGATO_AREA
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA
from anagrafica.permessi.applicazioni import REFERENTE

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO, GESTIONE_AUTOPARCHI_SEDE, \
    GESTIONE_GRUPPI_SEDE, GESTIONE_GRUPPO, GESTIONE_AREE_SEDE, GESTIONE_REFERENTI_ATTIVITA, \
    GESTIONE_CENTRALE_OPERATIVA_SEDE, EMISSIONE_TESSERINI, GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE


def permessi_persona(persona):
    """
    Permessi di ogni persona (nessuna delega).

    :param persona: La persona.
    :return: Lista di permessi.
    """
    from anagrafica.models import Sede
    from attivita.models import Attivita, Partecipazione
    from base.utils import poco_fa

    # Limiti di tempo per la centrale operativa
    quindici_minuti_fa = poco_fa() - timedelta(minutes=Attivita.MINUTI_CENTRALE_OPERATIVA)
    tra_quindici_minuti = poco_fa() + timedelta(minutes=Attivita.MINUTI_CENTRALE_OPERATIVA)

    # Sedi per le quali sto effettuando un servizio di centrale operativa
    sede_centrale_operativa = Sede.objects.filter(
        Partecipazione.con_esito(Partecipazione.ESITO_OK,
                                 persona=persona,
                                 ).via("attivita__turni__partecipazioni"),
        Q(
            Q(attivita__centrale_operativa=Attivita.CO_AUTO)
            | Q(attivita__centrale_operativa=Attivita.CO_MANUALE,
                attivita__turni__partecipazioni__centrale_operativa=True)
        ),
        attivita__turni__inizio__lte=tra_quindici_minuti,
        attivita__turni__fine__gte=quindici_minuti_fa,
    )

    return [
        (GESTIONE_CENTRALE_OPERATIVA_SEDE, sede_centrale_operativa)
    ]


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
        + permessi_responsabile_autoparco(sede) \
        + permessi_delegato_centrale_operativa(sede)


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
    from anagrafica.costanti import REGIONALE
    return [
        (GESTIONE_SOCI,         sede.espandi(includi_me=True)),
        (ELENCHI_SOCI,          sede.espandi(includi_me=True, pubblici=True)),
        (EMISSIONE_TESSERINI,   sede.queryset_modello().filter(estensione=REGIONALE)),
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
    attivita = Attivita.objects.filter(sede__in=sede_espansa)
    return [
        (GESTIONE_ATTIVITA_SEDE,        sede_espansa),
        (GESTIONE_ATTIVITA_AREA,        Area.objects.filter(sede__in=sede_espansa)),
        (GESTIONE_REFERENTI_ATTIVITA,   attivita),
        (GESTIONE_ATTIVITA,             attivita),
        (GESTIONE_GRUPPI_SEDE,          sede_espansa),
        (GESTIONE_GRUPPO,               Gruppo.objects.filter(sede__in=sede_espansa)),
        (GESTIONE_AREE_SEDE,            sede_espansa),
    ]


def permessi_delegato_obiettivo_1(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=1))


def permessi_delegato_obiettivo_2(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=2))


def permessi_delegato_obiettivo_3(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=3))


def permessi_delegato_obiettivo_4(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=4))


def permessi_delegato_obiettivo_5(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=5))


def permessi_delegato_obiettivo_6(sede):
    from attivita.models import Area
    sede_espansa = sede.espandi(includi_me=True)
    return [

           ] + \
           permessi_delegato_area(Area.objects.filter(sede__in=sede_espansa, obiettivo=6))


def permessi_referente_gruppo(gruppo):
    """
    Permessi della delega di REFERENTE DI GRUPPO.

    :param gruppo: Gruppo di cui si e' referenti.
    :return: Lista di permessi.
    """
    from gruppi.models import Gruppo
    return [
        (GESTIONE_GRUPPO,           gruppo.queryset_modello())
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
    if isinstance(area, QuerySet):
        qs_area = area
    else:
        qs_area = area.queryset_modello()
    attivita = Attivita.objects.filter(area=area)
    return [
        (GESTIONE_ATTIVITA_AREA,        qs_area),
        (GESTIONE_ATTIVITA,             attivita),
        (GESTIONE_REFERENTI_ATTIVITA,   attivita),
    ]


def permessi_delegato_centrale_operativa(sede):
    sede_espansa = sede.espandi(includi_me=True)
    return [
        (GESTIONE_CENTRALE_OPERATIVA_SEDE,          sede_espansa),
        (GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE,   sede_espansa),
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
    (DELEGATO_CO,               permessi_delegato_centrale_operativa),
    (RESPONSABILE_AREA,         permessi_responsabile_area),
    (REFERENTE,                 permessi_referente),
    (DIRETTORE_CORSO,           permessi_direttore_corso),
    (RESPONSABILE_AUTOPARCO,    permessi_responsabile_autoparco),
    (REFERENTE_GRUPPO,          permessi_referente_gruppo),
    (DELEGATO_OBIETTIVO_1,      permessi_delegato_obiettivo_1),
    (DELEGATO_OBIETTIVO_2,      permessi_delegato_obiettivo_2),
    (DELEGATO_OBIETTIVO_3,      permessi_delegato_obiettivo_3),
    (DELEGATO_OBIETTIVO_4,      permessi_delegato_obiettivo_4),
    (DELEGATO_OBIETTIVO_5,      permessi_delegato_obiettivo_5),
    (DELEGATO_OBIETTIVO_6,      permessi_delegato_obiettivo_6),
    (RESPONSABILE_FORMAZIONE,   permessi_responsabile_formazione),
)

# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_FUNZIONI_DICT = dict(PERMESSI_FUNZIONI)