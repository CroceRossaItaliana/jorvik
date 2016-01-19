# coding=utf-8


"""
Questo file gestisce i permessi in Gaia.
 ============================================================================================
 |                                    ! HEEEEY, TU !                                        |
 ============================================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione a:
   https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ============================================================================================
"""
from anagrafica.permessi.applicazioni import PRESIDENTE, DELEGATO_AREA, RESPONSABILE_AREA, REFERENTE, DIRETTORE_CORSO, \
    RESPONSABILE_AUTOPARCO, REFERENTE_GRUPPO
from anagrafica.permessi.applicazioni import UFFICIO_SOCI

GESTIONE_SEDE = "GESTIONE_SEDE"
GESTIONE_SOCI = "GESTIONE_SOCI"
ELENCHI_SOCI = "ELENCHI_SOCI"
GESTIONE_ATTIVITA_SEDE = "GESTIONE_ATTIVITA_SEDE"
GESTIONE_ATTIVITA_AREA = "GESTIONE_ATTIVITA_AREA"
GESTIONE_ATTIVITA = "GESTIONE_ATTIVITA"
GESTIONE_CORSI_SEDE = "GESTIONE_CORSI_SEDE"
GESTIONE_CORSO = "GESTIONE_CORSO"
GESTIONE_AUTOPARCHI_SEDE = "GESTIONE_AUTOPARCHI_SEDE"
GESTIONE_GRUPPI_SEDE = "GESTIONE_GRUPPI_SEDE"
GESTIONE_GRUPPO = "GESTIONE_GRUPPO"

# Tipologia degli oggetti assegnati ad ogni Permesso.
PERMESSI_OGGETTI = (
    (GESTIONE_SEDE,             ('anagrafica', 'Sede')),
    (GESTIONE_SOCI,             ('anagrafica', 'Sede')),
    (ELENCHI_SOCI,              ('anagrafica', 'Sede')),
    (GESTIONE_ATTIVITA_SEDE,    ('anagrafica', 'Sede')),
    (GESTIONE_ATTIVITA_AREA,    ('attivita',   'Area')),
    (GESTIONE_ATTIVITA,         ('attivita',   'Attivita')),
    (GESTIONE_CORSI_SEDE,       ('anagrafica', 'Sede')),
    (GESTIONE_CORSO,            ('formazione', 'CorsoBase')),
    (GESTIONE_AUTOPARCHI_SEDE,  ('anagrafica', 'Sede')),
    (GESTIONE_GRUPPI_SEDE,      ('anagrafica', 'Sede')),
    (GESTIONE_GRUPPO,           ('gruppi',     'Gruppo'))
)

# Tipologia degli oggetti assegnati ad ogni Delega.
DELEGHE_OGGETTI = (
    (PRESIDENTE,                'Sede'),
    (UFFICIO_SOCI,              'Sede'),
    (DELEGATO_AREA,             'Area'),
    (RESPONSABILE_AREA,         'Area'),
    (REFERENTE,                 'Attivita'),
    (DIRETTORE_CORSO,           'Corso'),
    (RESPONSABILE_AUTOPARCO,    'Sede'),
    (REFERENTE_GRUPPO,          'Gruppo'),
)


# Livelli di permesso
# IMPORTANTE: Tenere in ordine, sia numerico che di linea.

# - Scrittura e cancellazione
COMPLETO = 40

# - Scrittura e gestione deleghe
GESTIONE = 35

# - Scrittura
MODIFICA = 30

# - Scrittura dei dettagli
MODIFICA_TURNI = 25
MODIFICA_LEZIONI = MODIFICA_TURNI

# - Sola lettura
LETTURA = 10

# - Nessuno
NESSUNO = 0


# Livelli di permesso per template
PERMESSI_TESTO = {
    "completo": COMPLETO,
    "modifica": MODIFICA,
    "lettura": LETTURA,
    "nessuno": NESSUNO,
}


# I permessi minimi per ogni tipo di oggetto.
#  Ad esempio, tutti i commenti sono pubblici. Ne segue,
#  che il permesso minimo per Commento sia LETTURA.
# Ove non specificato, il minimo e' NESSUNO.
# Utilizzare permesso_minimo(Tipo) per ottenere il minimo.
PERMESSI_MINIMO = {
 'Persona':   NESSUNO,
 'Sede':      LETTURA,
 'Commento':  LETTURA,
}

def permesso_minimo(tipo):
    """
    Ritoran il permesso minimo globale per un detemrinato tipo.
    :param tipo: Un modello (ie. Persona, Sede, ecc.)
    :return: Il minimo, ie. NESSUNO o il minimo impostato.
    """
    tipo = tipo.__name__
    try:
        return PERMESSI_MINIMO[tipo]
    except KeyError:  # TOFIX
        return NESSUNO





# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_OGGETTI_DICT = dict(PERMESSI_OGGETTI)
DELEGHE_OGGETTI_DICT = dict(DELEGHE_OGGETTI)

# Costanti URL
ERRORE_PERMESSI = '/errore/permessi/'
ERRORE_ORFANO = '/errore/orfano/'