from collections import OrderedDict


# Tipologie di applicativi esistenti
PRESIDENTE = 'PR'
VICE_PRESIDENTE = 'VP'
COMMISSARIO = 'CM'
CONSIGLIERE = 'CN'
CONSIGLIERE_GIOVANE = 'CG'
CONSIGLIERE_GIOVANE_COOPTATO = 'CC'
UO_FORMAZIONE = 'UF'
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
DELEGATO_OBIETTIVO_7 = 'O7'
DELEGATO_OBIETTIVO_8 = 'O8'
RESPONSABILE_AREA = 'RA'
REFERENTE = 'RE'
REFERENTE_SERVIZI_SO = 'RS'
REFERENTE_OPERAZIONE_SO = 'RO'
REFERENTE_FUNZIONE_SO = 'RU'
REFERENTE_GRUPPO = 'GR'
DELEGATO_CO = 'CO'
DELEGATO_SO = 'SO'
RESPONSABILE_FORMAZIONE = 'RF'
RESPONSABILE_AUTOPARCO = 'AP'
RESPONSABILE_PATENTI = 'PA'
RESPONSABILE_DONAZIONI = 'DO'
DIRETTORE_CORSO = 'DC'
RESPONSABILE_EVENTO = 'EF'
# Non è una delega ma solo un segna posto per la rubriva
GIOVANI = 'GO'
REFERENTE_ZOOM = 'RZ'
CENTRO_FORMAZIONE_NAZIONALE = 'FN'


OBIETTIVI = {
    1: DELEGATO_OBIETTIVO_1,
    2: DELEGATO_OBIETTIVO_2,
    3: DELEGATO_OBIETTIVO_3,
    4: DELEGATO_OBIETTIVO_4,
    5: DELEGATO_OBIETTIVO_5,
    6: DELEGATO_OBIETTIVO_6,
    7: DELEGATO_OBIETTIVO_7,
    8: DELEGATO_OBIETTIVO_8,
}

# Nomi assegnati
PERMESSI_NOMI = (
    (PRESIDENTE,                "Presidente"),
    (VICE_PRESIDENTE,           "Vice Presidente"),
    (COMMISSARIO,               "Commissario"),
    (CONSIGLIERE,               "Consigliere"),
    (CONSIGLIERE_GIOVANE,       "Consigliere Rappresentante dei Giovani"),
    (CONSIGLIERE_GIOVANE_COOPTATO,       "Consigliere Rappresentante dei Giovani Cooptato"),
    (UO_FORMAZIONE,             "UO Formazione"),
    (UFFICIO_SOCI,              "Ufficio Soci"),
    (UFFICIO_SOCI_CM,           "Ufficio Soci corpo militare"),
    (UFFICIO_SOCI_IIVV,         "Ufficio Soci Infermiere volontarie"),
    (UFFICIO_SOCI_UNITA,        "Ufficio Soci Unità territoriali"),
    (DELEGATO_AREA,             "Delegato d'Area"),
    (DELEGATO_OBIETTIVO_1,      "Salute"),
    (DELEGATO_OBIETTIVO_2,      "Inclusione Sociale"),
    (DELEGATO_OBIETTIVO_3,      "Operazioni, Emergenza e Soccorsi"),
    (DELEGATO_OBIETTIVO_4,      "Principi e Valori Umanitari"),
    (DELEGATO_OBIETTIVO_5,      "Coordinatore attività per i Giovani"),
    (DELEGATO_OBIETTIVO_6,      "Innovazione, Volontariato e Formazione"),
    (DELEGATO_OBIETTIVO_7,      "Cooperazione internazionale decentrata"),
    (DELEGATO_OBIETTIVO_8,      "Riduzione del rischio da disastri e resilienza"),
    (RESPONSABILE_AREA,         "Responsabile d'Area"),
    (REFERENTE,                 "Referente Attività"),
    (REFERENTE_SERVIZI_SO,      "Referente Servizio SO"),
    (REFERENTE_OPERAZIONE_SO,   "Referente Operazione SO"),
    (REFERENTE_FUNZIONE_SO,     "Referente Operazione SO"),
    (REFERENTE_GRUPPO,          "Referente Gruppo"),
    (DELEGATO_CO,               "Delegato Centrale Operativa"),
    (DELEGATO_SO,               "Delegato Sala Operativa"),
    (RESPONSABILE_FORMAZIONE,   "Responsabile Formazione"),
    (DIRETTORE_CORSO,           "Direttore Corso"),
    (RESPONSABILE_EVENTO,       "Responsabile Evento"),
    (RESPONSABILE_AUTOPARCO,    "Responsabile Autoparco"),
    (REFERENTE_ZOOM,            "Referente Zoom"),
    (CENTRO_FORMAZIONE_NAZIONALE, "Centro Formazione Nazionale"),
    #(RESPONSABILE_PATENTI,      "Responsabile Patenti"),
    #(RESPONSABILE_DONAZIONI,    "Responsabile Donazioni Sangue"),
)

DELEGHE_RUBRICA = (
    PRESIDENTE, COMMISSARIO, CONSIGLIERE_GIOVANE, CONSIGLIERE_GIOVANE_COOPTATO, UFFICIO_SOCI, UFFICIO_SOCI_UNITA,
    DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3,
    DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, DELEGATO_OBIETTIVO_7, DELEGATO_OBIETTIVO_8,
    RESPONSABILE_FORMAZIONE, DELEGATO_CO, DELEGATO_SO, RESPONSABILE_AUTOPARCO, GIOVANI
)

PERMESSI_NOMI_DICT = dict(PERMESSI_NOMI)

RUBRICHE_TITOLI = OrderedDict((
    ('presidenti', (PRESIDENTE, 'Presidenti', True)),
    ('commissari', (COMMISSARIO, 'Commissari', True)),
    ('condigliere_giovane', (CONSIGLIERE_GIOVANE, 'Consiglieri Rappresentanti dei Giovani', True)),
    ('consigliere_giovane_cooptato', (CONSIGLIERE_GIOVANE_COOPTATO, 'Consiglieri Rappresentanti dei Giovani Cooptato', True)),
    ('giovani', (GIOVANI, 'Giovani', True)),
    ('delegati_us', (UFFICIO_SOCI, 'Delegati Ufficio Soci', True)),
    ('delegati_us_unita', (UFFICIO_SOCI_UNITA, 'Delegati Ufficio Soci Unità territoriali', True)),
    ('delegati_us_corpo_militare', (UFFICIO_SOCI_CM, 'Delegati Ufficio Soci Corpo militare', True)),
    ('delegati_us_infermiere_volontarie', (UFFICIO_SOCI_IIVV, 'Delegati Ufficio Infermiere Volontarie', True)),
    ('delegati_obiettivo_1', (DELEGATO_OBIETTIVO_1, 'Salute', True)),
    ('delegati_obiettivo_2', (DELEGATO_OBIETTIVO_2, 'Inclusione Sociale', True)),
    ('delegati_obiettivo_3', (DELEGATO_OBIETTIVO_3, 'Operazioni, Emergenza e Soccorsi', True)),
    ('delegati_obiettivo_4', (DELEGATO_OBIETTIVO_4, 'Principi e Valori Umanitari', True)),
    ('delegati_obiettivo_5', (DELEGATO_OBIETTIVO_5, 'Coordinatore attività per i Giovani', True)),
    ('delegati_obiettivo_6', (DELEGATO_OBIETTIVO_6, 'Innovazione, Volontariato e Formazione', True)),
    ('delegati_area', (DELEGATO_AREA, 'Delegati Area', False)),
    # ('responsabili_area', (RESPONSABILE_AREA, 'Responsabili d\'Area', False)), rimosso perché non utile al momento
    ('referenti_attivita', (REFERENTE, 'Referenti Attività', False)),
    ('referenti_gruppi', (REFERENTE, 'Referenti Gruppi', False)),
    # ('referenti_servizio_so', (REFERENTE_SERVIZI_SO, 'Referenti Servizi SO', False)),
    # ('referenti_operazione_so', (REFERENTE_OPERAZIONE_SO, 'Referenti Operazione SO', False)),
    # ('referenti_funzioni_so', (REFERENTE_FUNZIONE_SO, 'Referenti Funzione SO', False)),
    ('centrali_operative', (DELEGATO_CO, 'Referenti Centrale Operativa', True)),
    ('sale_operative', (DELEGATO_SO, 'Delegati Sale Operativa', True)),
    ('responsabili_formazione', (RESPONSABILE_FORMAZIONE, 'Referenti Responsabili Formazione', True)),
    ('direttori_corsi', (DIRETTORE_CORSO, 'Direttori Corsi', True)),
    ('responsabili_autoparco', (RESPONSABILE_AUTOPARCO, 'Responsabili Autoparco', True)),
))

DELEGATI_NON_SONO_UN_BERSAGLIO = [PRESIDENTE, COMMISSARIO, DELEGATO_OBIETTIVO_4]
