from collections import OrderedDict


# Tipologie di applicativi esistenti
PRESIDENTE = 'PR'
VICE_PRESIDENTE = 'VP'
COMMISSARIO = 'CM'
CONSIGLIERE = 'CN'
CONSIGLIERE_GIOVANE = 'CG'
UFFICIO_SOCI = 'US'
UFFICIO_SOCI_CM = 'UM'
UFFICIO_SOCI_IIVV = 'IV'
UFFICIO_SOCI_UNITA = 'UU'
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
REFERENTE_SO = 'RS'
REFERENTE_GRUPPO = 'GR'
DELEGATO_CO = 'CO'
DELEGATO_SO = 'SO'
RESPONSABILE_FORMAZIONE = 'RF'
RESPONSABILE_AUTOPARCO = 'AP'
RESPONSABILE_PATENTI = 'PA'
RESPONSABILE_DONAZIONI = 'DO'
DIRETTORE_CORSO = 'DC'

OBIETTIVI = {
    1: DELEGATO_OBIETTIVO_1,
    2: DELEGATO_OBIETTIVO_2,
    3: DELEGATO_OBIETTIVO_3,
    4: DELEGATO_OBIETTIVO_4,
    5: DELEGATO_OBIETTIVO_5,
    6: DELEGATO_OBIETTIVO_6,
}

# Nomi assegnati
PERMESSI_NOMI = (
    (PRESIDENTE,                "Presidente"),
    (VICE_PRESIDENTE,           "Vice Presidente"),
    (COMMISSARIO,               "Commissario"),
    (CONSIGLIERE,               "Consigliere"),
    (CONSIGLIERE_GIOVANE,       "Consigliere giovane"),
    (UFFICIO_SOCI,              "Ufficio Soci"),
    (UFFICIO_SOCI_CM,           "Ufficio Soci corpo militare"),
    (UFFICIO_SOCI_IIVV,         "Ufficio Soci Infermiere volontarie"),
    (UFFICIO_SOCI_UNITA,        "Ufficio Soci Unità territoriali"),
    (DELEGATO_AREA,             "Delegato d'Area"),
    (DELEGATO_OBIETTIVO_1,      "Delegato Obiettivo I (Salute)"),
    (DELEGATO_OBIETTIVO_2,      "Delegato Obiettivo II (Sociale)"),
    (DELEGATO_OBIETTIVO_3,      "Delegato Obiettivo III (Emergenze)"),
    (DELEGATO_OBIETTIVO_4,      "Delegato Obiettivo IV (Principi)"),
    (DELEGATO_OBIETTIVO_5,      "Delegato Obiettivo V (Giovani)"),
    (DELEGATO_OBIETTIVO_6,      "Delegato Obiettivo VI (Sviluppo)"),
    (RESPONSABILE_AREA,         "Responsabile d'Area"),
    (REFERENTE,                 "Referente Attività"),
    (REFERENTE_SO,              "Referente Servizio SO"),
    (REFERENTE_GRUPPO,          "Referente Gruppo"),
    (DELEGATO_CO,               "Delegato Centrale Operativa"),
    (DELEGATO_SO,               "Delegato Sala Operativa"),
    (RESPONSABILE_FORMAZIONE,   "Responsabile Formazione"),
    (DIRETTORE_CORSO,           "Direttore Corso"),
    (RESPONSABILE_AUTOPARCO,    "Responsabile Autoparco"),
    #(RESPONSABILE_PATENTI,      "Responsabile Patenti"),
    #(RESPONSABILE_DONAZIONI,    "Responsabile Donazioni Sangue"),
)

DELEGHE_RUBRICA = (
    PRESIDENTE, COMMISSARIO, CONSIGLIERE_GIOVANE, UFFICIO_SOCI, UFFICIO_SOCI_UNITA,
    DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3,
    DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6,
    RESPONSABILE_FORMAZIONE, DELEGATO_CO, DELEGATO_SO, RESPONSABILE_AUTOPARCO,
)

PERMESSI_NOMI_DICT = dict(PERMESSI_NOMI)

RUBRICHE_TITOLI = OrderedDict((
    ('presidenti', (PRESIDENTE, 'Presidenti', True)),
    ('commissari', (COMMISSARIO, 'Commissari', True)),
    ('condigliere_giovane', (CONSIGLIERE_GIOVANE, 'Consiglieri giovani', True)),
    ('delegati_us', (UFFICIO_SOCI, 'Delegati Ufficio Soci', True)),
    ('delegati_us_unita', (UFFICIO_SOCI_UNITA, 'Delegati Ufficio Soci Unità territoriali', True)),
    ('delegati_us_corpo_militare', (UFFICIO_SOCI_CM, 'Delegati Ufficio Soci Corpo militare', True)),
    ('delegati_us_infermiere_volontarie', (UFFICIO_SOCI_IIVV, 'Delegati Ufficio Infermiere Volontarie', True)),
    ('delegati_obiettivo_1', (DELEGATO_OBIETTIVO_1, 'Delegati Obiettivo I (Salute)', True)),
    ('delegati_obiettivo_2', (DELEGATO_OBIETTIVO_2, 'Delegati Obiettivo II (Sociale)', True)),
    ('delegati_obiettivo_3', (DELEGATO_OBIETTIVO_3, 'Delegati Obiettivo III (Emergenze)', True)),
    ('delegati_obiettivo_4', (DELEGATO_OBIETTIVO_4, 'Delegati Obiettivo IV (Principi)', True)),
    ('delegati_obiettivo_5', (DELEGATO_OBIETTIVO_5, 'Delegati Obiettivo V (Giovani)', True)),
    ('delegati_obiettivo_6', (DELEGATO_OBIETTIVO_6, 'Delegati Obiettivo VI (Sviluppo)', True)),
    ('delegati_area', (DELEGATO_AREA, 'Delegati Area', False)),
    # ('responsabili_area', (RESPONSABILE_AREA, 'Responsabili d\'Area', False)), rimosso perché non utile al momento
    ('referenti_attivita', (REFERENTE, 'Referenti Attività', False)),
    ('referenti_gruppi', (REFERENTE, 'Referenti Gruppi', False)),
    ('referenti_so', (REFERENTE_SO, 'Referenti Servizi SO', False)),
    ('centrali_operative', (DELEGATO_CO, 'Referenti Centrale Operativa', True)),
    ('sale_operative', (DELEGATO_SO, 'Delegati Sale Operativa', True)),
    ('responsabili_formazione', (RESPONSABILE_FORMAZIONE, 'Referenti Responsabili Formazione', True)),
    ('direttori_corsi', (DIRETTORE_CORSO, 'Direttori Corsi', True)),
    ('responsabili_autoparco', (RESPONSABILE_AUTOPARCO, 'Responsabili Autoparco', True)),
))

DELEGATI_NON_SONO_UN_BERSAGLIO = [PRESIDENTE, COMMISSARIO, DELEGATO_OBIETTIVO_4]
