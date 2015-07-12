# coding=utf-8

__author__ = 'alfioemanuele'

# Tipologie di applicativi esistenti

PRESIDENTE = 'PR'
UFFICIO_SOCI = 'US'
DELEGATO_AREA = 'DA'
RESPONSABILE_AREA = 'RA'
REFERENTE = 'RE'

# Nomi assegnati
PERMESSI_NOMI = (
    (PRESIDENTE,        "Presidente"),
    (UFFICIO_SOCI,      "Ufficio Soci"),
    (DELEGATO_AREA,     "Delegato d'Area"),
    (RESPONSABILE_AREA, "Responsabile d'Area"),
    (REFERENTE,         "Referente Attività"),
)

# Slug applicazioni
APPLICAZIONI_SLUG = (
    (PRESIDENTE, "presidente"),
    (UFFICIO_SOCI, "ufficio-soci"),
    (DELEGATO_AREA, "delegato-area"),
    (RESPONSABILE_AREA, "responsabile-area"),
    (REFERENTE, "referente-attivita"),
)

PERMESSI_NOMI_DICT = dict(PERMESSI_NOMI)
APPLICAZIONI_SLUG_DICT = dict(APPLICAZIONI_SLUG)