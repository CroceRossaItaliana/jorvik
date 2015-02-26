"""
Questo file gestisce i permessi in Gaia.
"""
from django.shortcuts import redirect
from anagrafica.modelli import *
from attivita.modelli import *
from .funzioni import *

# ====================================================================
# |                           HEEEEY, TU!                            |
# ====================================================================
# | Leggi README.md per una guida su come aggiungere nuovi permessi. |
# ====================================================================

# Tipologie di applicativi esistenti

PRESIDENTE = 'PR'
VICEPRESIDENTE = 'VP'
UFFICIO_SOCI = 'US'
DELEGATO_AREA = 'DA'
RESPONSABILE_AREA = 'RA'
REFERENTE = 'RE'

# Nomi assegnati
PERMESSI_NOMI = (
    (PRESIDENTE,        "Presidente"),
    (VICEPRESIDENTE,    "Vice Presidente"),
    (UFFICIO_SOCI,      "Ufficio Soci"),
    (DELEGATO_AREA,     "Delegato d'Area"),
    (RESPONSABILE_AREA, "Responsabile d'Area"),
    (REFERENTE,         "Referente Attività"),
)

# Oggetti assegnati
PERMESSI_OGGETTI = (
    (PRESIDENTE,        Comitato),
    (VICEPRESIDENTE,    Comitato),
    (UFFICIO_SOCI,      Comitato),
    (DELEGATO_AREA,     Area),
    (RESPONSABILE_AREA, Area),
    (REFERENTE,         Attivita),
)

# Livelli di permesso
SCRITTURA = 10
LETTURA = 5

# Funzioni permessi
# Nota bene: Non inserire () dopo il nome della funzione.
PERMESSI_FUNZIONI = (
    (PRESIDENTE,        permessi_presidente),
    (VICEPRESIDENTE,    permessi_vicepresidente),
    (UFFICIO_SOCI,      permessi_ufficio_soci),
    (DELEGATO_AREA,     permessi_delegato_area),
    (RESPONSABILE_AREA, permessi_responsabile_area),
    (REFERENTE,         permessi_referente),
)

# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_NOMI_DICT = dict(PERMESSI_NOMI)
PERMESSI_OGGETTI_DICT = dict(PERMESSI_OGGETTI)
PERMESSI_FUNZIONI_DICT = dict(PERMESSI_FUNZIONI)

# Il redirect in caso di permessi negati
PERMESSO_NEGATO = redirect('/?accesso-negato=1')

# Qui inizia la magia nera.
# Non toccare a meno che tu sappia cosa stai facendo.


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

    if not isinstance(instanza_delega.oggetto, PERMESSI_OGGETTI_DICT[tipo]):
        raise ValueError("Il tipo di oggetto associato non è valido per questa delega")

    return PERMESSI_FUNZIONI_DICT[tipo](instanza_delega.oggetto, oggetto)


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


def permessi_persona(persona, oggetto):
    """
    Restituisce il livello di permessi di una persona o None se nessuno.

    :param persona: La persona.
    :param oggetto: L'oggetto.
    :return: Una costante di livello di permessi o None.
    """
    deleghe = persona.deleghe_attuali()
    return permessi_deleghe(deleghe, oggetto)


def permessi_minimi_persona(persona, oggetto, minimo=LETTURA):
    """
    Controlla se una persona ha i permessi minimi per accedere ad un oggetto.

    :param persona: La persona da testare per i permessi.
    :param oggetto: L'oggetto da accedere
    :param permessi: Il permesso richiesto, es. SCRITTURA.
    :return: Vero se il permesso minimo e' raggiunto, falso altrimenti.
    """
    permessi = permessi_persona(persona, oggetto)

    if not permessi:
        return False

    return permessi >= minimo

