import datetime
from datetime import datetime
from anagrafica.costanti import TERRITORIALE, REGIONALE, LOCALE, PROVINCIALE

ANNI_DI_RIFERIMENTO = 10


def get_years():
    l = []
    current_year = datetime.now().year
    for i in range(0, ANNI_DI_RIFERIMENTO):
        year = "{}/{}".format(current_year - i, current_year - i - 1)
        l.append(
            (current_year - i, year)
        )
    return l


def get_type():
    return [(k, v) for k, v in STATISTICA.items()]


'''
    VALORI STATISTICHE
'''
GENERALI = 'generali'
NUM_SOCI_VOL = 'num_soci_vol'
NUM_VOL_M_F = 'num_vol_m_f'
NUM_VOL_FASCIA_ETA = 'num_vol_fascia_eta'
NUM_NUOVI_VOL = 'num_nuovi_vol'
NUM_DIMESSI = 'num_dimessi'
NUM_SEDI = 'num_sedi'
NUM_SEDI_NUOVE = 'num_sedi_nuove'
NUMERO_CORSI = 'num_corsi'
IIVV_CM = 'iivv_cm'
ORE_SERVIZIO = 'ore_servizio'

'''
    NOMI VISUALIZZATI STATISTICHE
'''
STATISTICA = {
    GENERALI: "Generali",
    NUM_SOCI_VOL: "Soci e Volontari",
    NUM_VOL_M_F: "Volontari M/F",
    NUM_VOL_FASCIA_ETA: "Volontari per fascia di età",
    NUM_NUOVI_VOL: "Nuovi volontari",
    NUM_DIMESSI: "Dimessi",
    NUM_SEDI: "Sedi",
    NUM_SEDI_NUOVE: "Sedi nuove",
    NUMERO_CORSI: "Corsi",
    IIVV_CM: "IIVV/CM",
    ORE_SERVIZIO: "Ore di Servizio"
}


FILTRO_ANNO = 'ANNO'
FILTRO_DATA = 'DATA'

TIPO_CHOICES = [
    (FILTRO_ANNO, 'Anno'),
    (FILTRO_DATA, 'Data'),
]

COMITATI_DA_EXLUDERE = ["Comitato dell'Area Metropolitana di Roma Capitale", ]

COLORI_COMITATI = {
    PROVINCIALE: '#C0C0C0',
    REGIONALE: '#FF0000',
    LOCALE: '#C0C0C0',
    TERRITORIALE: '#00FFFF',
}

