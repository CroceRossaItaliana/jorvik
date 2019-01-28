from anagrafica.models import Appartenenza, Persona, Sede
from anagrafica.costanti import TERRITORIALE, REGIONALE, NAZIONALE, LOCALE, ESTENDIONI_DICT
import datetime

'''
    OGNI FUNZIONE DOVRA AVERE QUESTO OUTPUT
    
    {
        "nome": @NOME DA VISUALIZZARE,
        "nazionali": @LISTA,
        "regionali": @LISTA,
        "locali": @LISTA,
        "territoriali": @LISTA 
        "tot": @LIST_TOT
    }
    
    @LISTA
    [
        {
            "comitato": @COMITATO,
            "statistiche": {
                @NOMEVALORE: @VALORE NUMERICO STATISTICA
            }
        }
    ]
    
    @LIST_TOT
    [
        {
            "nome": @Comitato
            "statistiche": {
                @NOMEVALORE: @VALORE NUMERICO STATISTICA
            }
        }
    ]
'''

'''
    STATISTICHE PER FASCI DI ETA
    Numero di volontari per fasce:
    14/18 - 18/25 - 25/32 - 32/45 - 45/60 - over 60
    per Ogni comitato Nazionale/Regione/locale/territoriale
'''
def statistica_num_vol_fascia_eta():

    nazionali = Sede.objects.filter(estensione=NAZIONALE)
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')
    locali = Sede.objects.filter(estensione=LOCALE)
    territoriali = Sede.objects.filter(estensione=TERRITORIALE)

    def get_num_vol_fascia_eta(comitati=None, figli=False):
        def count(query, min=0, max=9999):
            i = 0
            for el in query:
                if el.eta >= min and el.eta <= max:
                    i += 1
            return i

        l = []

        for el in comitati:
            persone = el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO)
            l.append(
                {
                    "comitato": el,
                    "statistiche": {
                        "Da 14 a 18:": count(persone, 14, 18),
                        "Da 18 a 25:": count(persone, 18, 25),
                        "Da 25 a 32:": count(persone, 25, 32),
                        "Da 32 a 45:": count(persone, 32, 45),
                        "Da 45 a 60:": count(persone, 54, 60),
                        "Over 60:": count(persone, 60),
                    }
                }
            )
        return l

    obj = {
        "nome": STATISTICA[NUM_VOL_M_F],
        "nazionali": get_num_vol_fascia_eta(nazionali, True),
        "regionali": get_num_vol_fascia_eta(regionali),
        "locali": get_num_vol_fascia_eta(locali),
        "territoriali": get_num_vol_fascia_eta(territoriali)
    }

    return obj


'''
    STATISTICA NUMERO M/F
    Numero di volontario divesi per sesso
    Per ogni comitato Nazionale/Regionale/Locale/Territoriale    
'''
def statistica_num_vol_m_f():

    nazionali = Sede.objects.filter(estensione=NAZIONALE)
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')
    locali = Sede.objects.filter(estensione=LOCALE)
    territoriali = Sede.objects.filter(estensione=TERRITORIALE)

    def get_m_f_statistiche(comitati=None, figli=False):
        l = []
        for el in comitati:
            persone = el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO)
            l.append(
                {
                    "comitato": el,
                    "statistiche": {
                        "M:": int(persone.filter(genere=Persona.MASCHIO).count()),
                        "F:": int(persone.filter(genere=Persona.FEMMINA).count())
                    }
                }
            )
        return l

    obj = {
        "nome": STATISTICA[NUM_VOL_M_F],
        "nazionali": get_m_f_statistiche(nazionali, True),
        "regionali": get_m_f_statistiche(regionali),
        "locali": get_m_f_statistiche(locali),
        "territoriali": get_m_f_statistiche(territoriali)
    }

    return obj


'''
    STATISTICA NUMERO DI SOCI/VOLONTARI
    Per Ogni comitato Regionale
    valori visibili per anno corrente/precedente
'''
def statistica_num_soci_vol():

    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')

    totale_regione_soci_currente = 0
    totale_regione_volontari_current = 0
    totale_regione_soci_before = 0
    totale_regione_volontari_before = 0

    regione_soci_volontari = []

    finish_current = datetime.datetime.now().date().replace(month=12, day=31)
    current_year = finish_current.year
    finish_before = finish_current.replace(year=finish_current.year - 1)
    before_year = finish_before.year

    for regione in regionali:
        regione_soci_current = int(
            regione.membri_attuali(
                figli=True, membro__in=Appartenenza.MEMBRO_SOCIO, creazione__lte=finish_current
            ).count()
        )
        regione_soci_before = int(
            regione.membri_attuali(
                figli=True, membro__in=Appartenenza.MEMBRO_SOCIO, creazione__lte=finish_before
            ).count()
        )
        regione_volontari_current = int(
            regione.membri_attuali(
                figli=True, membro=Appartenenza.VOLONTARIO, creazione__lte=finish_current
            ).count()
        )
        regione_volontari_before = int(
            regione.membri_attuali(
                figli=True, membro=Appartenenza.VOLONTARIO, creazione__lte=finish_before
            ).count()
        )

        regione_soci_volontari += [
            {
                "comitato": regione,
                "statistiche": {
                    "Soci al {}:".format(current_year): regione_soci_current,
                    "Volontari al {}:".format(current_year): regione_volontari_current,
                    "Soci al {}:".format(before_year): regione_soci_before,
                    "Volontari al {}:".format(before_year): regione_volontari_before,
                }
            }
        ]
        totale_regione_soci_currente += regione_soci_current
        totale_regione_volontari_current += regione_volontari_current
        totale_regione_soci_before += regione_soci_before
        totale_regione_volontari_before += regione_volontari_before

    obj = {
        "nome": STATISTICA[NUM_SOCI_VOL],
        "nazionali": None,
        "regionali": regione_soci_volontari,
        "locali": None,
        "territoriali": None,
        "tot": [
            {
                "nome": "Regionale",
                "statistiche": {
                    "Totale Soci al {}".format(current_year): totale_regione_soci_currente,
                    "Totale Volontari al {}".format(current_year): totale_regione_volontari_current,
                    "Totale Soci al {}".format(before_year): totale_regione_soci_before,
                    "Totale Volontari al {}".format(before_year): totale_regione_volontari_before,
                },
            }
        ]
    }

    return obj


'''
    STATISTICHE GENERALI (DEFAULT)
    persone_numero
    soci_numero
    soci_percentuale
    soci_giovani_35_numero
    soci_giovani_35_percentuale
    sedi_numero
    comitati_numero
    totale_regione_soci
    totale_regione_volontari
'''
def statistica_generale():
    oggi = datetime.date.today()
    nascita_minima_35 = datetime.date(oggi.year - 36, oggi.month, oggi.day)
    persone = Persona.objects.all()

    soci = Persona.objects.filter(
        Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_SOCIO).via("appartenenze")
    ).distinct('nome', 'cognome', 'codice_fiscale')
    soci_giovani_35 = soci.filter(
        data_nascita__gt=nascita_minima_35,
    )

    sedi = Sede.objects.filter(attiva=True)
    comitati = sedi.comitati()

    obj = {
        "persone_numero": persone.count(),
        "soci_numero": soci.count(),
        "soci_percentuale": soci.count() / persone.count() * 100,
        "soci_giovani_35_numero": soci_giovani_35.count(),
        "soci_giovani_35_percentuale": soci_giovani_35.count() / soci.count() * 100,
        "sedi_numero": sedi.count(),
        "comitati_numero": comitati.count()
    }
    return obj


'''
    STATISTICHE NUMERO NUOVI VOLONTARI
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistica_num_nuovi_vol():

    def get_tot(start=None, finish=None, estensione=None):

        current_year = start.year
        before_year = start.replace(year=current_year - 1).year

        current = Appartenenza.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            terminazione=None,
            membro=Appartenenza.VOLONTARIO,
            sede__estensione=estensione,
        )

        before = Appartenenza.objects.filter(
            creazione__gte=start.replace(year=start.year - 1),
            creazione__lte=finish.replace(year=finish.year - 1),
            terminazione=None,
            membro=Appartenenza.VOLONTARIO,
            sede__estensione=estensione,
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale nuovi volontari al {}'.format(current_year): current.count(),
                'Totale nuovi volontari al {}'.format(before_year): before.count()
            }
        }

    start = datetime.datetime.now().date().replace(month=1, day=1)
    finish = datetime.datetime.now().date().replace(month=12, day=31)

    obj = {
        "nome": STATISTICA[NUM_NUOVI_VOL],
        "nazionali": None,
        "regionali": None,
        "locali": None,
        "territoriali": None,
        "tot": [
            get_tot(start, finish, NAZIONALE),
            get_tot(start, finish, REGIONALE),
            get_tot(start, finish, LOCALE),
            get_tot(start, finish, TERRITORIALE),
        ]
    }

    return obj


'''
    STATISTICA NUMERO DIMESSI
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistica_num_dimessi():

    def get_tot(start=None, finish=None, estensione=None):

        current_year = start.year
        before_year = current_year - 1

        current = Appartenenza.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            terminazione=Appartenenza.DIMISSIONE,
            sede__estensione=estensione,
        )

        before = Appartenenza.objects.filter(
            creazione__gte=start.replace(year=before_year),
            creazione__lte=finish.replace(year=before_year),
            terminazione=Appartenenza.DIMISSIONE,
            sede__estensione=estensione,
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale al {}'.format(current_year): current.count(),
                'Totale al {}'.format(before_year): before.count()
            }
        }

    start = datetime.datetime.now().date().replace(month=1, day=1)
    finish = datetime.datetime.now().date().replace(month=12, day=31)

    obj = {
        "nome": STATISTICA[NUM_DIMESSI],
        "nazionali": None,
        "regionali": None,
        "locali": None,
        "territoriali": None,
        "tot": [
            get_tot(start, finish, NAZIONALE),
            get_tot(start, finish, REGIONALE),
            get_tot(start, finish, LOCALE),
            get_tot(start, finish, TERRITORIALE),
        ]
    }

    return obj


'''
    STATISTICHE NUMERO SEDI
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistica_num_sedi():

    def get_tot(current=None, before=None, estensione=None):

        current_attivo = Sede.objects.filter(
            creazione__lte=current,
            estensione=estensione,
            attiva=True
        )

        current_disattivo = Sede.objects.filter(
            creazione__lte=current,
            estensione=estensione,
            attiva=False
        )

        before_attivo = Sede.objects.filter(
            creazione__lte=before,
            estensione=estensione,
            attiva=True
        )

        before_disattivo = Sede.objects.filter(
            creazione__lte=before,
            estensione=estensione,
            attiva=False
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale attivo {}'.format(current.year): current_attivo.count(),
                'Totale disattivo {}'.format(current.year): current_disattivo.count(),
                'Totale attivo {}'.format(before.year): before_attivo.count(),
                'Totale disattivo {}'.format(before.year): before_disattivo.count(),
            }
        }

    current = datetime.datetime.now().replace(day=31, month=12)
    before = current.replace(year=current.year - 1)

    obj = {
        "nome": STATISTICA[NUM_DIMESSI],
        "nazionali": None,
        "regionali": None,
        "locali": None,
        "territoriali": None,
        "tot": [
            get_tot(current, before, NAZIONALE),
            get_tot(current, before, REGIONALE),
            get_tot(current, before, LOCALE),
            get_tot(current, before, TERRITORIALE),
        ]
    }

    return obj


'''
    STATISTICHE NUMERO NUOVE SEDI
    numero di nuove sedi nell'anno corrente/precedente
    
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistiche_num_sedi_nuove():

    def get_tot(start=None, finish=None, estensione=None):

        current_year = start.year
        before_year = start.replace(year=current_year - 1).year

        current = Sede.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            estensione=estensione,
            attiva=True
        )

        before = Sede.objects.filter(
            creazione__gte=start.replace(year=before_year),
            creazione__lte=finish.replace(year=before_year),
            estensione=estensione,
            attiva=True
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale nuove sedi al {}'.format(current_year): current.count(),
                'Totale nuove sedi al {}'.format(before_year): before.count(),
            }
        }

    start = datetime.datetime.now().date().replace(month=1, day=1)
    finish = datetime.datetime.now().date().replace(month=12, day=31)

    obj = {
        "nome": STATISTICA[NUM_SEDI_NUOVE],
        "nazionali": None,
        "regionali": None,
        "locali": None,
        "territoriali": None,
        "tot": [
            get_tot(start, finish, NAZIONALE),
            get_tot(start, finish, REGIONALE),
            get_tot(start, finish, LOCALE),
            get_tot(start, finish, TERRITORIALE),
        ]
    }

    return obj


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

'''
    NOMI VISUALIZZATI STATISTICHE
'''
STATISTICA = {
    GENERALI: "Generali",
    NUM_SOCI_VOL: "Soci e Volontari",
    NUM_VOL_M_F: "Volontari M/F",
    NUM_VOL_FASCIA_ETA: "Volontari per fasciati di età",
    NUM_NUOVI_VOL: "Nuovi volontari",
    NUM_DIMESSI: "Dimessi",
    NUM_SEDI: "Sedi",
    NUM_SEDI_NUOVE: "Sedi nuove"
}

'''
    FUNZIONI CHE CALCOLANO LE STATISTICHE
'''
FUNZIONI_STATISTICHE = {
    GENERALI: statistica_generale,
    NUM_VOL_M_F: statistica_num_vol_m_f,
    NUM_SOCI_VOL: statistica_num_soci_vol,
    NUM_VOL_FASCIA_ETA: statistica_num_vol_fascia_eta,
    NUM_NUOVI_VOL: statistica_num_nuovi_vol,
    NUM_DIMESSI: statistica_num_dimessi,
    NUM_SEDI: statistica_num_sedi,
    NUM_SEDI_NUOVE: statistiche_num_sedi_nuove
}
