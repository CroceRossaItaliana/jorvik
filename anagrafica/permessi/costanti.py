# coding=utf-8


"""
Questo file gestisce i permessi in Gaia.
"""
from anagrafica.permessi.applicazioni import PRESIDENTE
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.applicazioni import DELEGATO_AREA
from anagrafica.permessi.applicazioni import RESPONSABILE_AREA
from anagrafica.permessi.applicazioni import REFERENTE

from anagrafica.permessi.funzioni import permessi_presidente, permessi_ufficio_soci, \
    permessi_delegato_area, permessi_responsabile_area, permessi_referente
from anagrafica.models import Sede
from attivita.models import Attivita, Area


# ====================================================================
# |                           HEEEEY, TU!                            |
# ====================================================================
# | Leggi README.md per una guida su come aggiungere nuovi permessi. |
# ====================================================================



# Oggetti assegnati
PERMESSI_OGGETTI = (
    (PRESIDENTE,        Sede),
    (UFFICIO_SOCI,      Sede),
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
    (UFFICIO_SOCI,      permessi_ufficio_soci),
    (DELEGATO_AREA,     permessi_delegato_area),
    (RESPONSABILE_AREA, permessi_responsabile_area),
    (REFERENTE,         permessi_referente),
)

# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_OGGETTI_DICT = dict(PERMESSI_OGGETTI)
PERMESSI_FUNZIONI_DICT = dict(PERMESSI_FUNZIONI)

# Il redirect in caso di permessi negati
PERMESSO_NEGATO = '/errore/accesso-negato/'
