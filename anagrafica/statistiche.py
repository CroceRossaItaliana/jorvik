from anagrafica.models import Appartenenza, Persona, Sede
from formazione.models import CorsoBase
from anagrafica.costanti import TERRITORIALE, REGIONALE, NAZIONALE, LOCALE, ESTENDIONI_DICT, PROVINCIALE
import datetime
from attivita.models import Attivita, Turno
from django.db.models import F, Sum
from datetime import timedelta, datetime
from django import forms
from curriculum.areas import OBBIETTIVI_STRATEGICI
from formazione.models import Titolo
from formazione.models import Corso


def get_statistica_collapse_ric(comitati, f, **kwargs):
    estensione = {NAZIONALE: REGIONALE, REGIONALE: LOCALE, LOCALE: TERRITORIALE, TERRITORIALE: None}
    obj = []
    for comitato in comitati:
        if comitato.estensione == REGIONALE:
            # trattare i provinciali come i locali ricordarsi che al di sotto dei provinciali ci sono i locali
            locali = Sede.objects.filter(estensione=LOCALE, genitore=comitato)
            provinciali = Sede.objects.filter(estensione=PROVINCIALE, genitore=comitato)
            locali = list(locali) + list(provinciali)
            for provinciale in provinciali:
                locali += list(Sede.objects.filter(genitore=provinciale, estensione=LOCALE))
            obj.append(
                {
                    "comitato": comitato,
                    "statistiche": f(comitato=comitato, **{'figli': True}),
                    "figli": get_statistica_collapse_ric(
                        comitati=locali, f=f, **kwargs
                    )
                }
            )
            continue
        elif comitato.estensione == PROVINCIALE:
            continue
        else:
            obj.append(
                {
                    "comitato": comitato,
                    "statistiche": f(comitato=comitato, **{'figli': True}),
                    "figli": get_statistica_collapse_ric(
                        comitati=Sede.objects.filter(
                            genitore=comitato, estensione=estensione[comitato.estensione]
                        ).exclude(nome__contains='Provinciale Di Roma') if estensione[comitato.estensione] else [],
                        f=f, **kwargs
                    )
                }
            )
    return obj


'''
    STATISTICHE PER FASCI DI ETA
    Numero di volontari per fasce:
    14/18 - 18/25 - 25/32 - 32/45 - 45/60 - over 60
    per Ogni comitato Nazionale/Regione/locale/territoriale
'''
def statistica_num_vol_fascia_eta(**kwargs):

    def get_num_vol_per_eta(comitato=None, **kwargs):

        def count(query, min=0, max=9999):
            i = 0
            for el in query:
                if el.eta >= min and el.eta <= max:
                    i += 1
            return i

        figli = kwargs.get('figli') if kwargs.get('figli') else False
        persone = comitato.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO)
        return {
            "Da 14 a 18": count(persone, 14, 18),
            "Da 18 a 25": count(persone, 18, 25),
            "Da 25 a 32": count(persone, 25, 32),
            "Da 32 a 45": count(persone, 32, 45),
            "Da 45 a 60": count(persone, 54, 60),
            "Over 60": count(persone, 60),
        }

    obj = {
        "nome": STATISTICA[NUM_VOL_M_F],
        "comitati": get_statistica_collapse_ric(
            comitati=Sede.objects.filter(estensione=NAZIONALE), f=get_num_vol_per_eta
        )
    }

    return obj


'''
    STATISTICA NUMERO M/F
    Numero di volontario divesi per sesso
    Per ogni comitato Nazionale/Regionale/Locale/Territoriale    
'''
def statistica_num_vol_m_f(**kwargs):

    def get_m_f_statistiche(comitato=None, **kwargs):
        figli = kwargs.get('figli') if kwargs.get('figli') else False
        persone = comitato.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO)

        return {
            "M": persone.filter(genere=Persona.MASCHIO).count(),
            "F": persone.filter(genere=Persona.FEMMINA).count()
        }

    obj = {
        "nome": STATISTICA[NUM_VOL_M_F],
        "comitati": get_statistica_collapse_ric(
            comitati=Sede.objects.filter(estensione=NAZIONALE), f=get_m_f_statistiche
        )
    }

    return obj


'''
    STATISTICA NUMERO DI SOCI/VOLONTARI
    Per Ogni comitato Regionale
    valori visibili per anno corrente/precedente
'''
def statistica_num_soci_vol(**kwargs):

    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')

    totale_regione_soci_currente = 0
    totale_regione_volontari_current = 0
    totale_regione_soci_before = 0
    totale_regione_volontari_before = 0

    regione_soci_volontari = []

    finish_current = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')))
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

    # Elimino la doppia presenza delle sede Area Metropolitana di Roma Capitale
    metropolitana_roma = Sede.objects.filter(nome="Comitato dell'Area Metropolitana di Roma Capitale").first()
    if metropolitana_roma:
        regione_soci_current = int(
            metropolitana_roma.membri_attuali(
                figli=False, membro__in=Appartenenza.MEMBRO_SOCIO, creazione__lte=finish_current
            ).count()
        )
        regione_soci_before = int(
            metropolitana_roma.membri_attuali(
                figli=False, membro__in=Appartenenza.MEMBRO_SOCIO, creazione__lte=finish_before
            ).count()
        )
        regione_volontari_current = int(
            metropolitana_roma.membri_attuali(
                figli=False, membro=Appartenenza.VOLONTARIO, creazione__lte=finish_current
            ).count()
        )
        regione_volontari_before = int(
            metropolitana_roma.membri_attuali(
                figli=False, membro=Appartenenza.VOLONTARIO, creazione__lte=finish_before
            ).count()
        )

        totale_regione_soci_currente -= regione_soci_current
        totale_regione_volontari_current -= regione_volontari_current
        totale_regione_soci_before -= regione_soci_before
        totale_regione_volontari_before -= regione_volontari_before

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
def statistica_generale(**kwargs):
    import datetime
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
def statistica_num_nuovi_vol(**kwargs):

    def get_tot_anno(start=None, finish=None, estensione=None):

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
        print(current.count(), before.count())

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale nuovi volontari al {}'.format(current_year): current.count(),
                'Totale nuovi volontari al {}'.format(before_year): before.count()
            }
        }

    def get_tot_date(start=None, finish=None, estensione=None):

        current = Appartenenza.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            terminazione=None,
            membro=Appartenenza.VOLONTARIO,
            sede__estensione=estensione,
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale nuovi volontari dal {} al {}'.format(start, finish): current.count()
            }
        }

    obj = {
        "nome": STATISTICA[NUM_NUOVI_VOL],
        "tot": []
    }

    tipo = kwargs.get('tipo_filtro')

    if tipo == FILTRO_ANNO:
        start = datetime.now().date().replace(month=1, day=1, year=int(kwargs.get('anno_di_riferimento')))
        finish = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')))
        obj['tot'] = [
            get_tot_anno(start, finish, NAZIONALE),
            get_tot_anno(start, finish, REGIONALE),
            get_tot_anno(start, finish, LOCALE),
            get_tot_anno(start, finish, TERRITORIALE),
        ]
    elif tipo == FILTRO_DATA:
        print(tipo)
        start = kwargs.get('dal')
        finish = kwargs.get('al')
        print(start, finish)
        obj['tot'] = [
            get_tot_date(start, finish, NAZIONALE),
            get_tot_date(start, finish, REGIONALE),
            get_tot_date(start, finish, LOCALE),
            get_tot_date(start, finish, TERRITORIALE),
        ]

    return obj


'''
    STATISTICA NUMERO DIMESSI
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistica_num_dimessi(**kwargs):

    def get_tot_anno(start=None, finish=None, estensione=None):

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

    def get_tot_date(start=None, finish=None, estensione=None):

        current = Appartenenza.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            terminazione=Appartenenza.DIMISSIONE,
            sede__estensione=estensione,
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale Volontari dimessi dal {} al {}'.format(start, finish): current.count()
            }
        }

    obj = {
        "nome": STATISTICA[NUM_DIMESSI],
        "tot": []
    }

    tipo = kwargs.get('tipo_filtro')

    if tipo == FILTRO_ANNO:
        start = datetime.now().date().replace(month=1, day=1, year=int(kwargs.get('anno_di_riferimento')))
        finish = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')))
        obj['tot'] = [
            get_tot_anno(start, finish, NAZIONALE),
            get_tot_anno(start, finish, REGIONALE),
            get_tot_anno(start, finish, LOCALE),
            get_tot_anno(start, finish, TERRITORIALE),
        ]
    elif tipo == FILTRO_DATA:
        start = kwargs.get('dal')
        finish = kwargs.get('al')
        obj['tot'] = [
            get_tot_date(start, finish, NAZIONALE),
            get_tot_date(start, finish, REGIONALE),
            get_tot_date(start, finish, LOCALE),
            get_tot_date(start, finish, TERRITORIALE),
        ]

    return obj


'''
    STATISTICHE NUMERO SEDI
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistica_num_sedi(**kwargs):

    def get_tot_anno(current=None, before=None, estensione=None):

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

    obj = {
        "nome": STATISTICA[NUM_SEDI],
        "tot": []
    }

    start = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')))
    finish = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento'))-1)
    obj['tot'] = [
        get_tot_anno(start, finish, NAZIONALE),
        get_tot_anno(start, finish, REGIONALE),
        get_tot_anno(start, finish, LOCALE),
        get_tot_anno(start, finish, TERRITORIALE),
    ]

    return obj


'''
    STATISTICHE NUMERO NUOVE SEDI
    numero di nuove sedi nell'anno corrente/precedente
    
    livello nazionale/regionale/locale/territoriale
    valori visibili per anno corrente/precedente
'''
def statistiche_num_sedi_nuove(**kwargs):

    def get_tot_anno(start=None, finish=None, estensione=None):

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

    def get_tot_date(start=None, finish=None, estensione=None):

        current = Sede.objects.filter(
            creazione__gte=start,
            creazione__lte=finish,
            estensione=estensione,
            attiva=True
        )

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                'Totale nuove sedi dal {} al {}'.format(start, finish): current.count()
            }
        }

    obj = {
        "nome": STATISTICA[NUM_SEDI_NUOVE],
        "tot": []
    }

    tipo = kwargs.get('tipo_filtro')

    if tipo == FILTRO_ANNO:
        start = datetime.now().date().replace(month=1, day=1, year=int(kwargs.get('anno_di_riferimento')))
        finish = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')))
        obj['tot'] = [
            get_tot_anno(start, finish, NAZIONALE),
            get_tot_anno(start, finish, REGIONALE),
            get_tot_anno(start, finish, LOCALE),
            get_tot_anno(start, finish, TERRITORIALE),
        ]
    elif tipo == FILTRO_DATA:
        start = kwargs.get('dal')
        finish = kwargs.get('al')
        obj['tot'] = [
            get_tot_date(start, finish, NAZIONALE),
            get_tot_date(start, finish, REGIONALE),
            get_tot_date(start, finish, LOCALE),
            get_tot_date(start, finish, TERRITORIALE),
        ]

    return obj


def statistica_num_corsi(**kwargs):

    def get_tot_anno(estensione=None, **kwargs):
        livello_riferimento = kwargs.get('livello_riferimento')
        nome_corso = kwargs.get('nome_corso')
        area_riferimento = kwargs.get('area_riferimento')
        anno = int(kwargs.get('anno_di_riferimento'))

        filter_name = lambda x: nome_corso in x.nome

        corsi_current = CorsoBase.objects.filter(
            anno=anno,
            sede__estensione=estensione,
            cdf_level=livello_riferimento,
            cdf_area=area_riferimento
        )

        corsi_before = CorsoBase.objects.filter(
            anno=anno-1,
            sede__estensione=estensione,
            cdf_level=livello_riferimento,
            cdf_area=area_riferimento
        )

        corsi_current_attivi = corsi_current.filter(stato=Corso.ATTIVO)
        corsi_current_disattivi = corsi_current.filter(stato=Corso.TERMINATO)
        corsi_before_attivi = corsi_before.filter(stato=Corso.ATTIVO)
        corsi_before_disattivi = corsi_before.filter(stato=Corso.TERMINATO)

        if nome_corso:
            corsi_current_attivi = filter(filter_name, corsi_current_attivi)
            corsi_current_disattivi = filter(filter_name, corsi_current_disattivi)
            corsi_before_attivi = filter(filter_name, corsi_before_attivi)
            corsi_before_disattivi = filter(filter_name, corsi_before_disattivi)

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                "Corsi nel {} Attivi".format(anno): len(list(corsi_current_attivi)),
                "Corsi nel {} Disattivi".format(anno): len(list(corsi_current_disattivi)),
                "Corsi nel {} Attivi".format(anno-1): len(list(corsi_before_attivi)),
                "Corsi nel {} Disattivi".format(anno-1): len(list(corsi_before_disattivi)),
            }
        }

    def get_tot_date(start=True, finish=True, estensione=None, **kwargs):
        livello_riferimento = kwargs.get('livello_riferimento')
        nome_corso = kwargs.get('nome_corso')
        area_riferimento = kwargs.get('area_riferimento')

        filter_name = lambda x: nome_corso in x.nome

        corsi = CorsoBase.objects.filter(
            creazione__lte=finish,
            creazione__gte=start,
            sede__estensione=estensione,
            cdf_level=livello_riferimento,
            cdf_area=area_riferimento
        )

        corsi_attivi = corsi.filter(stato=Corso.ATTIVO)
        corsi_disattivi = corsi.filter(stato=Corso.TERMINATO)

        if nome_corso:
            corsi_attivi = filter(filter_name, corsi_attivi)
            corsi_disattivi = filter(filter_name, corsi_disattivi)

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                "Corsi Attivi dal {} al {}".format(start, finish): len(list(corsi_attivi)),
                "Corsi Disattivi dal {} al {}".format(start, finish): len(list(corsi_disattivi))
            }
        }

    obj = {
        "nome": STATISTICA[NUMERO_CORSI],
        "tot": []
    }

    tipo = kwargs.get('tipo_filtro')

    if tipo == FILTRO_ANNO:
        obj['tot'] = [
            get_tot_anno(estensione=NAZIONALE),
            get_tot_anno(estensione=REGIONALE),
            get_tot_anno(estensione=LOCALE),
            get_tot_anno(estensione=TERRITORIALE),
        ]
    elif tipo == FILTRO_DATA:
        start = kwargs.get('dal')
        finish = kwargs.get('al')
        obj['tot'] = [
            get_tot_date(start=start, finish=finish, estensione=NAZIONALE),
            get_tot_date(start=start, finish=finish, estensione=REGIONALE),
            get_tot_date(start=start, finish=finish, estensione=LOCALE),
            get_tot_date(start=start, finish=finish, estensione=TERRITORIALE),
        ]

    return obj


'''
    STATISTICHE IIVV/CM

    livello nazionale/regionale/locale/territoriale
'''
def statistica_iivv_cm(**kwargs):

    def get_iivv_cm(comitato, **kwargs):
        figli = kwargs.get('figli') if kwargs.get('figli') else False
        membri_iv_n = comitato.membri_attuali(figli=figli).filter(iv=True)
        membri_cm_n = comitato.membri_attuali(figli=figli).filter(cm=True)

        return {
            "IIVV": membri_iv_n.count(),
            "CM": membri_cm_n.count(),
        }

    obj = {
        "nome": STATISTICA[IIVV_CM],
        "comitati": get_statistica_collapse_ric(
            comitati=Sede.objects.filter(estensione=NAZIONALE), f=get_iivv_cm
        )
    }

    return obj


'''
    STATISTICHE ORE DI SERVIZIO

    livello nazionale/regionale/locale/territoriale
'''
def statistica_ore_servizio(**kwargs):

    def get_tot(estensione=None, inizio=None, fine=None):

        sedi = Sede.objects.filter(estensione=estensione)

        qs_attivita = Attivita.objects.filter(
            stato=Attivita.VISIBILE,
            sede__in=sedi
        )
        qs_turni = Turno.objects.filter(
            attivita__in=qs_attivita,
            inizio__lte=datetime.now().date().replace(month=1, day=1),
            fine__gte=datetime.now().date().replace(month=12, day=31)
        )

        ore_di_servizio = qs_turni.annotate(durata=F('fine') - F('inizio')).aggregate(totale_ore=Sum('durata'))['totale_ore'] or timedelta()

        return {
            "nome": ESTENDIONI_DICT[estensione],
            "statistiche": {
                "Ore di servizio": ore_di_servizio
            }
        }


    obj = {
        "nome": STATISTICA[ORE_SERVIZIO],
        "tot": [
            get_tot(NAZIONALE),
            get_tot(REGIONALE),
            get_tot(LOCALE),
            get_tot(TERRITORIALE),
        ]
    }

    return obj


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
    NUM_VOL_FASCIA_ETA: "Volontari per fasciati di età",
    NUM_NUOVI_VOL: "Nuovi volontari",
    NUM_DIMESSI: "Dimessi",
    NUM_SEDI: "Sedi",
    NUM_SEDI_NUOVE: "Sedi nuove",
    NUMERO_CORSI: "Corsi",
    IIVV_CM: "IIVV/CM",
    ORE_SERVIZIO: "Ore di Servizio"
}


'''
    FUNZIONI CHE CALCOLANO LE STATISTICHE
'''
STATISTICHE = {
    GENERALI: (statistica_generale, ('statistiche_generali.html', )),
    NUM_VOL_M_F: (statistica_num_vol_m_f, ('statistiche_per_comitati_collapse.html', )),
    NUM_SOCI_VOL: (statistica_num_soci_vol, ('statistiche_per_comitati.html', 'statistiche_totali.html', )), # TODO da rifare completamente
    NUM_VOL_FASCIA_ETA: (statistica_num_vol_fascia_eta, ('statistiche_per_comitati_collapse.html', )),
    NUM_NUOVI_VOL: (statistica_num_nuovi_vol, ('statistiche_totali.html', )),
    NUM_DIMESSI: (statistica_num_dimessi, ('statistiche_totali.html', )),
    NUM_SEDI: (statistica_num_sedi, ('statistiche_totali.html', )),# TODO qua è inpensabile che di utilizzare il range di date
    NUM_SEDI_NUOVE: (statistiche_num_sedi_nuove, ('statistiche_totali.html', )),
    NUMERO_CORSI: (statistica_num_corsi, ('statistiche_totali.html', )),
    IIVV_CM: (statistica_iivv_cm, ('statistiche_per_comitati_collapse.html', )),
    ORE_SERVIZIO: (statistica_ore_servizio, ('statistiche_totali.html', )),
}

FILTRO_ANNO = 'ANNO'
FILTRO_DATA = 'DATA'

TIPO_CHOICES = [
    (FILTRO_ANNO, 'Anno'),
    (FILTRO_DATA, 'Data'),
]

class ModuloStatisticheBase(forms.Form):
    tipo_statistiche = forms.ChoiceField(widget=forms.Select(), choices=get_type(), required=True)
    nome_corso = forms.CharField(required=False)
    livello_riferimento = forms.ChoiceField(widget=forms.Select(), choices=Titolo.CDF_LIVELLI, required=False)
    area_riferimento = forms.ChoiceField(widget=forms.Select(), choices=OBBIETTIVI_STRATEGICI, required=False)
    tipo_filtro = forms.ChoiceField(choices=TIPO_CHOICES, initial=FILTRO_ANNO, widget=forms.RadioSelect())
    anno_di_riferimento = forms.ChoiceField(widget=forms.Select(), choices=get_years(), required=False)
    dal = forms.DateField(required=False)
    al = forms.DateField(required=False)
