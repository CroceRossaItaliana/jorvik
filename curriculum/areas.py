TITOLO_STUDIO_CHOICES = [
    (0, 'Licenza elementare'),
    (1, 'Licenza media'),
    (2, 'Operatore'),
    (3, 'Diploma'),
    (4, 'Laurea triennale'),
    (5, 'Laurea magistrale'),
    (6, 'Specializzazione'),
]


PATENTE_CIVILE_CHOICES = [
    (0, 'Patente'),
    (1, 'Certificato di abilitazione professionale'),
]


# Area a cui appartiene titolo (dati allineati al doc. elenco_corsi.xls)
OBBIETTIVO_STRATEGICO_SALUTE = '1'
OBBIETTIVO_STRATEGICO_SOCIALE = '2'
OBBIETTIVO_STRATEGICO_EMERGENZA = '3'
OBBIETTIVO_STRATEGICO_ADVOCACY = '4'
OBBIETTIVO_STRATEGICO_GIOVANI = '5'
OBBIETTIVO_STRATEGICO_SVILUPPO = '6'
OBBIETTIVO_STRATEGICO_MIGRAZIONI = '7'
OBBIETTIVO_STRATEGICO_COOPERAZIONI_INT = '8'
OBBIETTIVO_STRATEGICO_SALUTE_SICUREZZA = '9'

OBBIETTIVI_STRATEGICI = [
    (OBBIETTIVO_STRATEGICO_SALUTE, 'Salute'),
    (OBBIETTIVO_STRATEGICO_SALUTE_SICUREZZA, 'Salute e sicurezza'),
    (OBBIETTIVO_STRATEGICO_SOCIALE, 'Inclusione Sociale'),
    (OBBIETTIVO_STRATEGICO_EMERGENZA, 'Emergenza'),
    (OBBIETTIVO_STRATEGICO_ADVOCACY, 'Principi e Valori'),
    (OBBIETTIVO_STRATEGICO_GIOVANI, 'Giovani'),
    (OBBIETTIVO_STRATEGICO_SVILUPPO, 'Sviluppo Organizzativo'),
    (OBBIETTIVO_STRATEGICO_MIGRAZIONI, 'Migrazioni'),
    (OBBIETTIVO_STRATEGICO_COOPERAZIONI_INT, 'Cooperazione Internazionale'),
]
