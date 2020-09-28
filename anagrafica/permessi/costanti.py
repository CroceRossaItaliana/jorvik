from ..permessi.applicazioni import (PRESIDENTE, DELEGATO_AREA, RESPONSABILE_AREA,
                                     REFERENTE, DIRETTORE_CORSO, RESPONSABILE_AUTOPARCO, REFERENTE_GRUPPO, COMMISSARIO,
                                     CONSIGLIERE, UFFICIO_SOCI, UFFICIO_SOCI_CM)

"""
                       Questo file gestisce i permessi in Gaia.
 ===============================================================================
 |                                   ! HEEEEY, TU !                            |
 ===============================================================================
 Prima di avventurarti da queste parti, assicurati di leggere la documentazione:
 https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ===============================================================================
"""


GESTIONE_SEDE = "GESTIONE_SEDE"
GESTIONE_SOCI = "GESTIONE_SOCI"
ELENCHI_SOCI = "ELENCHI_SOCI"
RUBRICA_UFFICIO_SOCI = "RUBRICA_UFFICIO_SOCI"
RUBRICA_UFFICIO_SOCI_UNITA = "RUBRICA_UFFICIO_SOCI_UNITA"
RUBRICA_PRESIDENTI = "RUBRICA_PRESIDENTI"
RUBRICA_COMMISSARI = "RUBRICA_COMMISSARI"
RUBRICA_CONSIGLIERE_GIOVANE = "RUBRICA_COMMISSARI"
RUBRICA_DELEGATI_AREA = "RUBRICA_DELEGATI_AREA"
RUBRICA_DELEGATI_OBIETTIVO_1 = "RUBRICA_DELEGATI_OBIETTIVO_1"
RUBRICA_DELEGATI_OBIETTIVO_2 = "RUBRICA_DELEGATI_OBIETTIVO_2"
RUBRICA_DELEGATI_OBIETTIVO_3 = "RUBRICA_DELEGATI_OBIETTIVO_3"
RUBRICA_DELEGATI_OBIETTIVO_4 = "RUBRICA_DELEGATI_OBIETTIVO_4"
RUBRICA_DELEGATI_OBIETTIVO_6 = "RUBRICA_DELEGATI_OBIETTIVO_6"
RUBRICA_DELEGATI_GIOVANI = "RUBRICA_DELEGATI_GIOVANI"
RUBRICA_RESPONSABILI_AREA = "RUBRICA_RESPONSABILI_AREA"
RUBRICA_REFERENTI_ATTIVITA = "RUBRICA_REFERENTI_ATTIVITA"
RUBRICA_REFERENTI_GRUPPI = "RUBRICA_REFERENTI_GRUPPI"
RUBRICA_CENTRALI_OPERATIVE = "RUBRICA_CENTRALI_OPERATIVE"
RUBRICA_RESPONSABILI_FORMAZIONE = "RUBRICA_RESPONSABILI_FORMAZIONE"
RUBRICA_DIRETTORI_CORSI = "RUBRICA_DIRETTORI_CORSI"
RUBRICA_RESPONSABILI_AUTOPARCO = "RUBRICA_RESPONSABILI_AUTOPARCO"
GESTIONE_ATTIVITA_SEDE = "GESTIONE_ATTIVITA_SEDE"
GESTIONE_ATTIVITA_AREA = "GESTIONE_ATTIVITA_AREA"
GESTIONE_AREE_SEDE = "GESTIONE_AREE_SEDE"
GESTIONE_ATTIVITA = "GESTIONE_ATTIVITA"
GESTIONE_REFERENTI_ATTIVITA = "GESTIONE_REFERENTI_ATTIVITA"
GESTIONE_CORSI_SEDE = "GESTIONE_CORSI_SEDE"
GESTIONE_CORSO = "GESTIONE_CORSO"
GESTIONE_AUTOPARCHI_SEDE = "GESTIONE_AUTOPARCHI_SEDE"
GESTIONE_GRUPPI_SEDE = "GESTIONE_GRUPPI_SEDE"
GESTIONE_GRUPPO = "GESTIONE_GRUPPO"
GESTIONE_GRUPPI = "GESTIONE_GRUPPI"
GESTIONE_CENTRALE_OPERATIVA_SEDE = "GESTIONE_CENTRALE_OPERATIVA_SEDE"
GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE = "GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE"
EMISSIONE_TESSERINI = "EMISSIONE_TESSERINI"
ASPIRANTE = "ASPIRANTE"

# Tipologia degli oggetti assegnati ad ogni Permesso.
PERMESSI_OGGETTI = (
    (GESTIONE_SEDE,             ('anagrafica', 'Sede')),
    (GESTIONE_SOCI,             ('anagrafica', 'Sede')),
    (ELENCHI_SOCI,              ('anagrafica', 'Sede')),
    (RUBRICA_UFFICIO_SOCI,      ('anagrafica', 'Sede')),
    (RUBRICA_UFFICIO_SOCI_UNITA,('anagrafica', 'Sede')),
    (RUBRICA_PRESIDENTI,        ('anagrafica', 'Sede')),
    (RUBRICA_COMMISSARI,       ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_AREA,     ('attivita', 'Area')),
    (RUBRICA_DELEGATI_OBIETTIVO_1,  ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_OBIETTIVO_2,  ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_OBIETTIVO_3,  ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_OBIETTIVO_4,  ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_OBIETTIVO_6,  ('anagrafica', 'Sede')),
    (RUBRICA_DELEGATI_GIOVANI,      ('anagrafica', 'Sede')),
    (RUBRICA_RESPONSABILI_AREA,     ('attivita', 'Area')),
    (RUBRICA_REFERENTI_ATTIVITA,    ('attivita', 'Attivita')),
    (RUBRICA_REFERENTI_GRUPPI,      ('anagrafica', 'Sede')),
    (RUBRICA_CENTRALI_OPERATIVE,    ('anagrafica', 'Sede')),
    (RUBRICA_RESPONSABILI_FORMAZIONE,   ('anagrafica', 'Sede')),
    (RUBRICA_DIRETTORI_CORSI,       ('formazione', 'CorsoBase')),
    (RUBRICA_RESPONSABILI_AUTOPARCO,    ('anagrafica', 'Sede')),
    (EMISSIONE_TESSERINI,       ('anagrafica', 'Sede')),
    (GESTIONE_ATTIVITA_SEDE,    ('anagrafica', 'Sede')),
    (GESTIONE_ATTIVITA_AREA,    ('attivita',   'Area')),
    (GESTIONE_REFERENTI_ATTIVITA,('attivita',   'Attivita')),
    (GESTIONE_ATTIVITA,         ('attivita',   'Attivita')),
    (GESTIONE_AREE_SEDE,        ('anagrafica', 'Sede')),
    (GESTIONE_CORSI_SEDE,       ('anagrafica', 'Sede')),
    (GESTIONE_CORSO,            ('formazione', 'CorsoBase')),
    (GESTIONE_AUTOPARCHI_SEDE,  ('anagrafica', 'Sede')),
    (GESTIONE_GRUPPI_SEDE,      ('anagrafica', 'Sede')),
    (GESTIONE_GRUPPO,           ('gruppi',     'Gruppo')),
    (GESTIONE_GRUPPI,           ('gruppi',     'Gruppo')),
    (GESTIONE_CENTRALE_OPERATIVA_SEDE,  ('anagrafica', 'Sede')),
    (GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE,  ('anagrafica', 'Sede')),
    (ASPIRANTE,                 ('formazione', 'InvitoCorsoBase')),
)

# Tipologia degli oggetti assegnati ad ogni Delega.
DELEGHE_OGGETTI = (
    (PRESIDENTE,                ('anagrafica', 'Sede', None)),
    (CONSIGLIERE,               ('anagrafica', 'Sede', None)),
    (COMMISSARIO,               ('anagrafica', 'Sede', None)),
    (UFFICIO_SOCI,              ('anagrafica', 'Sede', None)),
    (UFFICIO_SOCI_CM,           ('anagrafica', 'Sede', None)),
    (DELEGATO_AREA,             ('attivita', 'Area', 'sede__in')),
    (RESPONSABILE_AREA,         ('attivita', 'Area', 'sede__in')),
    (REFERENTE,                 ('attivita', 'Attivita', 'sede__in')),
    (DIRETTORE_CORSO,           ('formazione', 'CorsoBase', 'sede__in')),
    (RESPONSABILE_AUTOPARCO,    ('anagrafica', 'Sede', None)),
    (REFERENTE_GRUPPO,          ('anagrafica', 'Gruppo', 'sede__in')),
)

RUBRICA_DELEGATI_OBIETTIVO_ALL = [RUBRICA_DELEGATI_OBIETTIVO_1,
                                  RUBRICA_DELEGATI_OBIETTIVO_2,
                                  RUBRICA_DELEGATI_OBIETTIVO_3,
                                  RUBRICA_DELEGATI_OBIETTIVO_4,
                                  RUBRICA_DELEGATI_OBIETTIVO_6,]


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
