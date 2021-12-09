TERRITORIALE = 'T'
LOCALE = 'L'
PROVINCIALE = 'P'
REGIONALE = 'R'
NAZIONALE = 'N'
ESTENSIONE = (
    (TERRITORIALE, 'Unità Territoriale'),
    (LOCALE, 'Sede Locale'),
    (PROVINCIALE, 'Sede Provinciale'),
    (REGIONALE, 'Sede Regionale'),
    (NAZIONALE, 'Sede Nazionale')
)

# Ad uso di comparazione
ESTENSIONE_MINORE = {
    TERRITORIALE: [],
    LOCALE: [TERRITORIALE],
    PROVINCIALE: [LOCALE, TERRITORIALE],
    REGIONALE: [PROVINCIALE, LOCALE, TERRITORIALE],
    NAZIONALE: [REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE]
}

LIMITE_ETA = 35
LIMITE_ANNI_ATTIVITA = 1

REGIONI_CON_SIGLE = {
    1: {'sigla': 'CN', 'nome': 'Comitato Nazionale',},
    1008: {'sigla': 'ABR', 'nome': 'Abruzzo',},
    109: {'sigla': 'BAS', 'nome': 'Basilicata',},
    761: {'sigla': 'CAL', 'nome': 'Calabria',},
    645: {'sigla': 'CAM', 'nome': 'Campania',},
    155: {'sigla': 'EMR', 'nome': 'Emilia-Romagna',},
    1074: {'sigla': 'FVG', 'nome': 'Friuli-Venezia Giulia',},
    524: {'sigla': 'LAZ', 'nome': 'Lazio',},
    253: {'sigla': 'LIG', 'nome': 'Liguria',},
    329: {'sigla': 'LOM', 'nome': 'Lombardia',},
    957: {'sigla': 'MAR', 'nome': 'Marche',},
    1393: {'sigla': 'MOL', 'nome': 'Molise',},
    1193: {'sigla': 'PIE', 'nome': 'Piemonte',},
    893: {'sigla': 'PUG', 'nome': 'Puglia',},
    493: {'sigla': 'SAR', 'nome': 'Sardegna',},
    2: {'sigla': 'SIC', 'nome': 'Sicilia',},
    1105: {'sigla': 'TOS',  'nome': 'Toscana',},
    1364: {'sigla': 'UMB',  'nome': 'Umbria',},
    1189: {'sigla': 'VDA', 'nome': "Valle d'Aosta",},
    835: {'sigla': 'VEN', 'nome': 'Veneto',},
    1416: {'sigla': 'TRE', 'nome': 'Provincia Autonoma Trento',},
    1409: {'sigla': 'BOL', 'nome': 'Provincia Autonoma Bolzano',},
}

MIMETYPE_TO_CHECK = ['application/csv', 'application/zip', 'application/vnd.oasis.opendocument.text',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
                    'text/plain', 'application/x-rar', 'image/png', 'image/jpg', 'image/jpeg', 'image/gif',
                    'text/rtf', 'image/tiff', 'application/pdf',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/octet-stream']

area_roma_capitale_coordinamento_pk=1638
area_roma_capitale_pk=525