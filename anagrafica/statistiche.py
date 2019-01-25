from anagrafica.models import Appartenenza, Persona, Sede
from anagrafica.costanti import TERRITORIALE, REGIONALE, NAZIONALE, LOCALE
import datetime

'''
    OGNI FUNZIONE DOVRA AVERE QUESTO OUTPUT
    
    {
        "nome": @NOME DA VISUALIZZARE,
        "nazionali": [
            {
                "comitato": @COMITATO,
                "statistiche": { @LISTA FI TUTTE LE STATISTICHE
                    @NOMEVALORE: @VALORE NUMERICO STATISTICA
                }
            }
        ],
        "regionali": @LISTA,
        "locali": @LISTA,
        "territoriali": @LISTA 
    }
    
    
'''


def statistica_num_vol_fascia_eta():
    nazionali = Sede.objects.filter(estensione=NAZIONALE)
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')
    locali = Sede.objects.filter(estensione=LOCALE)
    territoriali = Sede.objects.filter(estensione=TERRITORIALE)

    def get_num_vol_fascia_eta(comitati=None, figli=False):
        l = []
        for el in comitati:
            l.append(
                {
                    "comitato": el,
                    "statistiche": {
                        "Da 14 a 18:": len(
                            [   p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >=14 and p.eta <= 18]
                        ),
                        "Da 18 a 25:": len(
                            [p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >=18 and p.eta <= 25]
                        ),
                        "Da 25 a 32:": len(
                            [p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >=25 and p.eta <= 32]
                        ),
                        "Da 32 a 45:": len(
                            [p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >=32 and p.eta <= 45]
                        ),
                        "Da 45 a 60:": len(
                            [p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >=45 and p.eta <= 69]
                        ),
                        "Over 60": len(
                            [p for p in el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO) if p.eta >= 60]
                        ),
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


def statistica_num_vol_m_f():

    nazionali = Sede.objects.filter(estensione=NAZIONALE)
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')
    locali = Sede.objects.filter(estensione=LOCALE)
    territoriali = Sede.objects.filter(estensione=TERRITORIALE)

    def get_m_f_statistiche(comitati=None, figli=False):
        l = []
        for el in comitati:
            l.append(
                {
                    "comitato": el,
                    "statistiche": {
                        "M:": int(el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO).filter(
                            genere=Persona.MASCHIO).count()),
                        "F:": int(el.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO).filter(
                            genere=Persona.FEMMINA).count())
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


def statistica_num_soci_vol():

    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')

    regione_soci_volontari = []
    for regione in regionali:
        regione_soci = int(regione.membri_attuali(figli=True, membro__in=Appartenenza.MEMBRO_SOCIO).count())
        regione_volontari = int(regione.membri_attuali(figli=True, membro=Appartenenza.VOLONTARIO).count())
        regione_soci_volontari += [
            {
                "comitato": regione,
                "statistiche": {
                    "Soci:": regione_soci,
                    "Volontari:": regione_volontari
                }
            }
        ]

    obj = {
        "nome": STATISTICA[NUM_SOCI_VOL],
        "nazionali": None,
        "regionali": regione_soci_volontari,
        "locali": None,
        "territoriali": None
    }

    return obj


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

    totale_regione_soci = 0
    totale_regione_volontari = 0

    obj = {
        "persone_numero": persone.count(),
        "soci_numero": soci.count(),
        "soci_percentuale": soci.count() / persone.count() * 100,
        "soci_giovani_35_numero": soci_giovani_35.count(),
        "soci_giovani_35_percentuale": soci_giovani_35.count() / soci.count() * 100,
        "sedi_numero": sedi.count(),
        "comitati_numero": comitati.count(),
        "totale_regione_soci": totale_regione_soci,
        "totale_regione_volontari": totale_regione_volontari,
    }
    return obj


'''
    VALOTI STATISTICHE
'''
GENERALI = 'generali'
NUM_SOCI_VOL = 'num_soci_vol'
NUM_VOL_M_F = 'num_vol_m_f'
NUM_VOL_FASCIA_ETA = 'num_vol_fascia_eta'

'''
    NOMI VISUALIZZARI STATISTICHE
'''
STATISTICA = {
    GENERALI: "Generali",
    NUM_SOCI_VOL: "Numero soci e Volontari",
    NUM_VOL_M_F: "Numero volontari M/F",
    NUM_VOL_FASCIA_ETA: "Numero volontari per fasciati di età",
}

'''
    FUNZIONI CHE CALCOLANO LE STATISTICHE
'''
FUNZIONI_STATISTICHE = {
        GENERALI: statistica_generale,
        NUM_VOL_M_F: statistica_num_vol_m_f,
        NUM_SOCI_VOL: statistica_num_soci_vol,
        NUM_VOL_FASCIA_ETA: statistica_num_vol_fascia_eta,
}
