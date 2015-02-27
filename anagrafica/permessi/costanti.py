"""
Questo file gestisce i permessi in Gaia.
"""
from django.shortcuts import redirect

from anagrafica.permessi.funzioni import permessi_presidente, permessi_vicepresidente, permessi_ufficio_soci, \
    permessi_delegato_area, permessi_responsabile_area, permessi_referente
from anagrafica.models import Comitato
from attivita.models import Attivita, Area


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
# IMPORTANTE: Tenere in ordine, sia numerico che di linea.

# - Scrittura e cancellazione
RIMOZIONE = 40

# - Scrittura
MODIFICA = 30

# - Scrittura dei dettagli
MODIFICA_TURNI = 25
MODIFICA_LEZIONI = MODIFICA_TURNI

# - Sola lettura
LETTURA = 10


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
