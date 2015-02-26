"""
Questo modulo contiene tutte le funzioni per testare i permessi
a partire da un oggetto sul quale ho una delega ed un oggetto da testare.
"""
from anagrafica.modelli import *


def permessi_presidente(comitato, oggetto):
    """
    Permessi della delega di PRESIDENTE.

    :param comitato: Il comitato di cui si e' presidenti.
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    # Se e' un comitato
    if isinstance(oggetto, Comitato):
        # Posso modificare se e' sotto il mio
        if oggetto.figlio_di(comitato):
            return SCRITTURA
        return None

    # Persona
    if isinstance(oggetto, Persona):
        # TODO: Assume che un presidente abbia permessi onnipotenti a scendere.
        if comitato.ha_persona(oggetto, comitati_figli=True):
            return SCRITTURA
        return None

    # Attivita
    if isinstance(oggetto, Attivita):
        # TODO: Assume che un presidente abbia permessi onnipotenti a scendere.
        if oggetto.figlio_di(comitato, comitati_figli=True):
            return SCRITTURA

    return None


def permessi_vicepresidente(comitato, oggetto):
    """
    Permessi della delega di VICE PRESIDENTE.

    :param comitato: Il comitato di cui si e' vice presidenti.
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    # Gli stessi permessi del presidente
    return permessi_presidente(comitato, oggetto)


def permessi_ufficio_soci(comitato, oggetto):
    """
    Permessi della delega di UFFICIO SOCI.

    :param comitato: Il comitato di cui si e' ufficio soci.
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    # L'ufficio soci e' il presidente nel contesto delle persone
    if isinstance(oggetto, Persona):
        return permessi_presidente(comitato, oggetto)

    return None


def permessi_delegato_area(area, oggetto):
    """
    Permessi della delega di DELEGATO D'AREA.

    :param area: L'area di cui si e' delegati
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    if isinstance(oggetto, Area):
        if oggetto == area:
            return SCRITTURA

    if isinstance(oggetto, Attivita):
        if oggetto.area == area:
            return SCRITTURA

    if isinstance(oggetto, Persona):
        # TODO: Controllare che la persona (oggetto) partecipi ad una attivita' dell'area
        if False:
            return LETTURA

    return None


def permessi_responsabile_area(area, oggetto):
    """
    Permessi della delega di RESPONSABILE D'AREA.

    :param area: L'area di cui si e' responsabili
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    return permessi_delegato_area(area, oggetto)


def permessi_referente(attivita, oggetto):
    """
    Permessi della delega di REFERENTE ATTIVITA'.

    :param attivita: L'attivita' di cui si e' referenti
    :param oggetto: L'oggetto per cui controllare i permessi.
    :return: SCRITTURA, LETTURA o None.
    """

    if isinstance(oggetto, Attivita):
        if attivita == oggetto:
            return SCRITTURA

    if isinstance(oggetto, Persona):
        # TODO: Controllare che la persona (oggetto) partecipi all'attivita'
        if False:
            return LETTURA

    return None


# Non modificare


def unisci_permessi(*args):
    """
    Unisce dei permessi ottenuti da funzioni permessi_* ed ottiene il permesso
    maggiore o None se nessun permesso ottenuto.
    :param *args: Tutti i permessi da unire.
    :return: Il permesso maggiore o nessuno.
    """

    permessi = [permesso for permesso in args if permesso is not None]

    # Se non e' rimasto niente, non ho permessi
    if not permessi:
        return None

    # Altrimenti, restituisci il permesso piu' alto
    return max(permessi)
