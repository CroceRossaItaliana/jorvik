# coding=utf-8

__author__ = 'alfioemanuele'

# Tipologie di applicativi esistenti

PRESIDENTE = 'PR'
UFFICIO_SOCI = 'US'
UFFICIO_SOCI_TEMPORANEO = 'UT'
DELEGATO_AREA = 'DA'
DELEGATO_OBIETTIVO_1 = 'O1'
DELEGATO_OBIETTIVO_2 = 'O2'
DELEGATO_OBIETTIVO_3 = 'O3'
DELEGATO_OBIETTIVO_4 = 'O4'
DELEGATO_OBIETTIVO_5 = 'O5'
DELEGATO_OBIETTIVO_6 = 'O6'
RESPONSABILE_AREA = 'RA'
REFERENTE = 'RE'
DELEGATO_CO = 'CO'
RESPONSABILE_FORMAZIONE = 'RF'
RESPONSABILE_AUTOPARCO = 'AP'
RESPONSABILE_PATENTI = 'PA'
RESPONSABILE_DONAZIONI = 'DO'
DIRETTORE_CORSO = 'DC'

# Nomi assegnati
PERMESSI_NOMI = (
    (PRESIDENTE,                "Presidente"),
    (UFFICIO_SOCI,              "Ufficio Soci"),
    (UFFICIO_SOCI_TEMPORANEO,   "Ufficio Soci Temporaneo"),
    (DELEGATO_AREA,             "Delegato d'Area"),
    (DELEGATO_OBIETTIVO_1,      "Delegato Obiettivo I (Salute)"),
    (DELEGATO_OBIETTIVO_2,      "Delegato Obiettivo II (Sociale)"),
    (DELEGATO_OBIETTIVO_3,      "Delegato Obiettivo III (Emergenze)"),
    (DELEGATO_OBIETTIVO_4,      "Delegato Obiettivo IV (Principi)"),
    (DELEGATO_OBIETTIVO_5,      "Delegato Obiettivo V (Giovani)"),
    (DELEGATO_OBIETTIVO_6,      "Delegato Obiettivo VI (Sviluppo)"),
    (RESPONSABILE_AREA,         "Responsabile d'Area"),
    (REFERENTE,                 "Referente Attività"),
    (DELEGATO_CO,               "Delegato Centrale Operativa"),
    (RESPONSABILE_FORMAZIONE,   "Responsabile Formazione"),
    (DIRETTORE_CORSO,           "Direttore Corso"),
    (RESPONSABILE_AUTOPARCO,    "Responsabile Autoparco"),
    (RESPONSABILE_PATENTI,      "Responsabile Patenti"),
    (RESPONSABILE_DONAZIONI,    "Responsabile Donazioni Sangue"),
)

# Slug applicazioni
APPLICAZIONI_SLUG = (
    (PRESIDENTE, "presidente"),
    (UFFICIO_SOCI, "ufficio-soci"),
    (DELEGATO_AREA, "delegato-area"),
    (RESPONSABILE_AREA, "responsabile-area"),
    (REFERENTE, "referente-attivita"),
    (DELEGATO_CO, "centrale-operativa"),
)

PERMESSI_NOMI_DICT = dict(PERMESSI_NOMI)
APPLICAZIONI_SLUG_DICT = dict(APPLICAZIONI_SLUG)