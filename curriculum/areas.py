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

OBBIETTIVI_STRATEGICI = [
    (OBBIETTIVO_STRATEGICO_SALUTE, 'Salute'),
    (OBBIETTIVO_STRATEGICO_SOCIALE, 'Sociale'),
    (OBBIETTIVO_STRATEGICO_EMERGENZA, 'Emergenza)'),
    (OBBIETTIVO_STRATEGICO_ADVOCACY, 'Advocacy e mediazione umanitaria'),
    (OBBIETTIVO_STRATEGICO_GIOVANI, 'Giovani'),
    (OBBIETTIVO_STRATEGICO_SVILUPPO, 'Sviluppo'),
]
