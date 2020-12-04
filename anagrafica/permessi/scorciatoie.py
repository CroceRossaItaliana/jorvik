from ..permessi.costanti import LETTURA, PERMESSI_OGGETTI_DICT
from ..permessi.funzioni import PERMESSI_FUNZIONI_DICT  #, unisci_permessi (not found)


def permessi_minimi_persona(persona, oggetto, minimo=LETTURA):
    """
    Controlla se una persona ha i permessi minimi per accedere ad un oggetto.

    :param persona: La persona da testare per i permessi.
    :param oggetto: L'oggetto da accedere
    :param permessi: Il permesso richiesto, es. MODIFICA.
    :return: Vero se il permesso minimo e' raggiunto, falso altrimenti.
    """
    permessi = permessi_persona(persona, oggetto)

    if not permessi:
        return False

    return permessi >= minimo


def permessi_persona(persona, oggetto):
    """
    Restituisce il livello di permessi di una persona o None se nessuno.

    :param persona: La persona.
    :param oggetto: L'oggetto.
    :return: Una costante di livello di permessi o None.
    """
    deleghe = persona.deleghe_attuali()
    return permessi_deleghe(deleghe, oggetto)


def permessi_deleghe(instanze_deleghe, oggetto):
    """
    Come permessi_delega, ma accetta piu' instanze di tipo delega.

    Ritorna il permesso maggiore ottenuto.
    :param instanze_deleghe: Un iterabile di instanze delega.
    :param oggetto: Oggetto.
    :return: Il permesso massimo o None se nessun permesso scaturisce.
    """

    # Ottiene tutti i permessi possibili
    permessi = [permessi_deleghe(x, oggetto) for x in instanze_deleghe]
    return unisci_permessi(*permessi)


def permessi_delega(instanza_delega, oggetto):
    """
    Questa funzione ha lo scopo di controllare, data una instanza di una delega
    (es. tizio e' ufficio soci presso questo posto) che livello di permessi
    vengono ottenuti come conseguenza nei confronti di un oggetto.

    :param instanza_delega: L'instanza della delega.
    :param oggetto: Oggetto.
    :return: Un livello di permesso o None se nessun permesso scaturisce.
    """
    tipo = instanza_delega.tipo

    if tipo not in PERMESSI_FUNZIONI_DICT:
        raise NotImplementedError("La delega non ha una funzione-permessi associata.")

    if tipo not in PERMESSI_OGGETTI_DICT:
        raise NotImplementedError("La delega non specifica la tipologia di oggetti associati.")

    if instanza_delega.oggetto.__class__.__name__ != PERMESSI_OGGETTI_DICT[tipo][1]:
        raise ValueError("Il tipo di oggetto associato non è valido per questa delega")

    # Controlla che la delega sia valida
    if not instanza_delega.attuale:
        return None

    return PERMESSI_FUNZIONI_DICT[tipo](instanza_delega.oggetto, oggetto)
