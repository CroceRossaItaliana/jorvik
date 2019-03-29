import datetime
from datetime import datetime
from anagrafica.costanti import TERRITORIALE, REGIONALE, LOCALE, PROVINCIALE
from collections import OrderedDict

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
STATISTICA = OrderedDict()
STATISTICA[GENERALI] = "Generali"
STATISTICA[NUM_VOL_M_F] = "Volontari M/F"
STATISTICA[NUM_SOCI_VOL] = "Soci e Volontari"
STATISTICA[NUM_VOL_FASCIA_ETA] = "Volontari per fascia di età"
STATISTICA[NUM_NUOVI_VOL] = "Nuovi volontari"
STATISTICA[NUM_DIMESSI] = "Dimessi"
STATISTICA[NUM_SEDI] = "Sedi"
STATISTICA[NUM_SEDI_NUOVE] = "Sedi nuove"
STATISTICA[NUMERO_CORSI] = "Corsi"
STATISTICA[IIVV_CM] = "IIVV/CM"
STATISTICA[ORE_SERVIZIO] = "Ore di Servizio"


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


QUERY_NUM_ORE = '''
            SELECT DISTINCT APP.id,B.n_person,
                CASE WHEN B.n_totale is null THEN 0
                    ELSE B.n_totale
                END AS n_totale,
                B.anno,
                APP.estensione
            FROM (
            SELECT DISTINCT A.id,B.persona_id,B.sede_id,C.estensione
            FROM anagrafica_persona A, anagrafica_appartenenza B, anagrafica_sede C
            WHERE A.id = B.persona_id
            AND B.sede_id = C.id
            AND B.confermata = true
            AND B.fine is null
            AND C.estensione = '{}'
            ) APP
                LEFT JOIN (
                SELECT DISTINCT A.*,H.estensione
                FROM (
                         SELECT E.persona_id, count(E.persona_id) as n_person, SUM(E.n_ore_lavorate) as n_totale, E.anno
                         FROM (
                                  SELECT C.*,
                                         (EXTRACT(HOURS FROM D.fine) - EXTRACT(HOURS FROM D.inizio)) AS n_ore_lavorate,
                                         EXTRACT(YEAR FROM D.inizio)                                 as anno
                                  FROM attivita_partecipazione C,
                                       attivita_turno D
                                  WHERE C.turno_id = D.id
                              ) E
                         GROUP BY E.persona_id, E.anno
                     )A, attivita_partecipazione B, attivita_turno F, attivita_attivita G, anagrafica_sede H
                WHERE A.persona_id = B.persona_id
                  AND B.turno_id = F.id
                  AND F.attivita_id = G.id
                  AND G.sede_id = H.id
                  AND B.confermata = true
                  AND A.anno = '{}'
            )B
            ON APP.id = B.persona_id
        '''
