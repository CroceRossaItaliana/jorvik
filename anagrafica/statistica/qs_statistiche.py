from anagrafica.models import Appartenenza, Persona, Sede, Partecipazione, Appartenenza
from formazione.models import CorsoBase
from anagrafica.costanti import TERRITORIALE, REGIONALE, NAZIONALE, LOCALE, ESTENDIONI_DICT, PROVINCIALE
import datetime
from datetime import datetime
from formazione.models import Corso
from django.db.models import Q, F, Sum
from .stat_costanti import (
    STATISTICA, COMITATI_DA_EXLUDERE, NUM_VOL_M_F, NUM_SOCI_VOL, NUM_NUOVI_VOL, FILTRO_ANNO, FILTRO_DATA,
    NUM_SEDI, NUM_DIMESSI, NUM_SEDI_NUOVE, NUMERO_CORSI, IIVV_CM, ORE_SERVIZIO, QUERY_NUM_ORE
)
from collections import OrderedDict
from django.db import connection


def formato_data(data):
    return data.strftime('%d-%m-%Y')


def get_statistica_collapse_ric(comitati, f, **kwargs):
    estensione = {NAZIONALE: REGIONALE, REGIONALE: LOCALE, PROVINCIALE: False, LOCALE: TERRITORIALE, TERRITORIALE: None}
    obj = []
    for comitato in comitati:
        if comitato.estensione == REGIONALE:
            # trattare i provinciali come i locali ricordarsi che al di sotto dei provinciali ci sono i locali
            locali = Sede.objects.filter(estensione=LOCALE, genitore=comitato, attiva=True)
            provinciali = Sede.objects.filter(estensione=PROVINCIALE, genitore=comitato, attiva=True)

            locali = list(locali) + list(provinciali)

            for provinciale in provinciali:
                locali += list(Sede.objects.filter(genitore=provinciale, estensione=LOCALE, attiva=True))

            obj.append(
                {
                    "comitato": comitato,
                    "statistiche": f(comitato=comitato, **{'figli': True}) if comitato.estensione != PROVINCIALE else f(comitato=comitato, **{'figli': False}),
                    "figli": get_statistica_collapse_ric(
                        comitati=locali, f=f, **kwargs
                    )
                }
            )
            continue
        else:
            obj.append(
                {
                    "comitato": comitato,
                    "statistiche": f(comitato=comitato, **{'figli': True}) if comitato.estensione != PROVINCIALE else f(comitato=comitato, **{'figli': False}),
                    "figli": get_statistica_collapse_ric(
                        comitati=Sede.objects.filter(
                            genitore=comitato, estensione=estensione[comitato.estensione], attiva=True
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
                if min <= el.eta <= max:
                    i += 1
            return i

        figli = kwargs.get('figli') if kwargs.get('figli') else False
        persone = comitato.membri_attuali(figli=figli, membro=Appartenenza.VOLONTARIO)
        result = OrderedDict()
        result["Da 14 a 18"] = count(persone, 14, 18)
        result["Da 18 a 25"] = count(persone, 18, 25)
        result["Da 25 a 32"] = count(persone, 25, 32)
        result["Da 32 a 45"] = count(persone, 32, 45)
        result["Da 45 a 60"] = count(persone, 45, 60)
        result["Over 60"] = count(persone, 60)
        return result

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
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(
        nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

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

    obj = {
        "nome": STATISTICA[NUM_SOCI_VOL],
        "regionali": regione_soci_volontari,
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

        start = formato_data(start)
        finish = formato_data(finish)

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
        start = formato_data(start)
        finish = formato_data(finish)
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
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

        current_disattivo = Sede.objects.filter(
            creazione__lte=current,
            estensione=estensione,
            attiva=False
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

        before_attivo = Sede.objects.filter(
            creazione__lte=before,
            estensione=estensione,
            attiva=True
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

        before_disattivo = Sede.objects.filter(
            creazione__lte=before,
            estensione=estensione,
            attiva=False
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

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
    finish = datetime.now().date().replace(month=12, day=31, year=int(kwargs.get('anno_di_riferimento')) - 1)
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
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

        before = Sede.objects.filter(
            creazione__gte=start.replace(year=before_year),
            creazione__lte=finish.replace(year=before_year),
            estensione=estensione,
            attiva=True
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))

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
        ).exclude(nome__contains=(Q(nome__contains=x) for x in COMITATI_DA_EXLUDERE))
        start = formato_data(start)
        finish = formato_data(finish)
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

        print(livello_riferimento, nome_corso, area_riferimento, kwargs.get('anno'))

        filter_name = lambda x: nome_corso in x.nome

        corsi_current = CorsoBase.objects.filter(
            anno=kwargs.get('anno'),
            sede__estensione=estensione,
            cdf_level=livello_riferimento,
            cdf_area=area_riferimento
        )

        corsi_before = CorsoBase.objects.filter(
            anno=kwargs.get('anno') - 1,
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
                "Corsi nel {} Terminati".format(anno): len(list(corsi_current_disattivi)),
                "Corsi nel {} Attivi".format(anno - 1): len(list(corsi_before_attivi)),
                "Corsi nel {} Terminati".format(anno - 1): len(list(corsi_before_disattivi)),
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
        start = formato_data(start)
        finish = formato_data(finish)
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
    anno = int(kwargs.get('anno_di_riferimento'))
    if tipo == FILTRO_ANNO:
        obj['tot'] = [
            get_tot_anno(estensione=NAZIONALE, anno=anno, **kwargs),
            get_tot_anno(estensione=REGIONALE, anno=anno, **kwargs),
            get_tot_anno(estensione=LOCALE, anno=anno, **kwargs),
            get_tot_anno(estensione=TERRITORIALE, anno=anno, **kwargs),
        ]
    elif tipo == FILTRO_DATA:
        start = kwargs.get('dal')
        finish = kwargs.get('al')
        obj['tot'] = [
            get_tot_date(start=start, finish=finish, estensione=NAZIONALE, **kwargs),
            get_tot_date(start=start, finish=finish, estensione=REGIONALE, **kwargs),
            get_tot_date(start=start, finish=finish, estensione=LOCALE, **kwargs),
            get_tot_date(start=start, finish=finish, estensione=TERRITORIALE, **kwargs),
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

    print(obj)

    return obj


'''
    STATISTICHE ORE DI SERVIZIO

    livello nazionale/regionale/locale/territoriale
'''


def statistica_ore_servizio(**kwargs):

    def get_tot(estensioni=[], inizio=None, fine=None, row=[], no_turni=[]):

        c_0, c_0_10, c_10_20, c_20_30, c_30, count = 0, 0, 0, 0, 0, 0
        c_0_b, c_0_10_b, c_10_20_b, c_20_30_b, c_30_b, count_b = 0, 0, 0, 0, 0, 0

        for el in row:
            for est in estensioni:
                if int(el['anno']) == inizio:
                    if el['estensione'] == est:
                        durata = el['durata'].seconds//3600
                        count += 1
                        if 0 < durata <= 10:
                            c_0_10 += 1
                        elif 10 < durata <= 20:
                            c_10_20 += 1
                        elif 20 < durata <= 30:
                            c_20_30 += 1
                        elif durata > 30:
                            c_30 += 1
                elif int(el['anno']) == fine:
                    if el['estensione'] == est:
                        durata = el['durata'].seconds//3600
                        count_b += 1
                        if 0 < durata <= 10:
                            c_0_10_b += 1
                        elif 10 < durata <= 20:
                            c_10_20_b += 1
                        elif 20 < durata <= 30:
                            c_20_30_b += 1
                        elif durata > 30:
                            c_30_b += 1


        statistica = OrderedDict([
            ("Uguale a 0h di servizio al {}".format(inizio), no_turni[0]-count),
            ("Da 0h a 10h di servizio al {}".format(inizio), c_0_10),
            ("Da 10h a 20h di servizio al {}".format(inizio), c_10_20),
            ("Da 20h a 30h di servizio al {}".format(inizio), c_20_30),
            ("Maggiore di 30h di servizio al {}".format(inizio), c_30),
            ('', ''),# per mantenere un spazio tra gli anni di riferimento
            ("Uguale a 0h di servizio al {}".format(fine), no_turni[0]-count_b),
            ("Da 0h a 10h di servizio al {}".format(fine), c_0_10_b),
            ("Da 10h a 20h di servizio al {}".format(fine), c_10_20_b),
            ("Da 20h a 30h di servizio al {}".format(fine), c_20_30_b),
            ("Maggiore di 30h di servizio al {}".format(fine), c_30_b),
        ])

        return {
            "nome": ESTENDIONI_DICT[estensioni[0]],
            "statistiche": statistica,
        }

    inizio = int(kwargs.get('anno_di_riferimento'))
    fine = int(kwargs.get('anno_di_riferimento'))-1

    p = Partecipazione.objects.select_related('turno').filter(
        Q(turno__inizio__year=fine) | Q(turno__inizio__year=inizio),
    ).extra({'anno': "Extract(year from attivita_turno.inizio)"}).values(
        'persona', 'turno__attivita__sede__estensione', 'anno'
    ).annotate(estensione=F('turno__attivita__sede__estensione'), durata=Sum(F('turno__fine') - F('turno__inizio')))

    storico_all = Partecipazione.objects.filter(
        turno__fine__gte=datetime.now().date().replace(month=1, day=1, year=fine),
        turno__inizio__lte=datetime.now().date().replace(month=12, day=12, year=inizio),
        confermata=True,
    )#.values_list('persona_id', flat=True)

    persone_all = Persona.objects.filter(
        Appartenenza.query_attuale(
            membro__in=Appartenenza.MEMBRO_ATTIVITA,
        ).via("appartenenze")
    )

    def calcola_no_turni(estensioni=[], storico_all=[], persone_all=[], inizio=None, fine=None):
        persone_all = persone_all.filter(
            Appartenenza.query_attuale(
                sede__estensione__in=estensioni
            ).via("appartenenze")
        )
        inizio = persone_all.exclude(pk__in=storico_all.filter(
            turno__fine__gte=datetime.now().date().replace(month=1, day=1, year=inizio),
            turno__inizio__lte=datetime.now().date().replace(month=12, day=12, year=inizio),
        ).values_list('persona_id', flat=True)).count()

        fine = persone_all.exclude(pk__in=storico_all.filter(
            turno__fine__gte=datetime.now().date().replace(month=1, day=1, year=fine),
            turno__inizio__lte=datetime.now().date().replace(month=12, day=12, year=fine),
        ).values_list('persona_id', flat=True)).count()

        return [inizio, fine]

    obj = {
        "nome": STATISTICA[ORE_SERVIZIO],
        "tot": [
            get_tot(
                [NAZIONALE], inizio, fine, p, calcola_no_turni(
                    [NAZIONALE], storico_all, persone_all, inizio, fine
                )
            ),
            get_tot(
                [REGIONALE], inizio, fine, p, calcola_no_turni(
                    [REGIONALE], storico_all, persone_all, inizio, fine
                )
            ),
            get_tot(
                [LOCALE, PROVINCIALE], inizio, fine, p, calcola_no_turni(
                    [LOCALE, PROVINCIALE], storico_all, persone_all, inizio, fine
                )
            ),
            get_tot(
                [TERRITORIALE], inizio, fine, p, calcola_no_turni(
                    [TERRITORIALE], storico_all, persone_all, inizio, fine
                )
            )
        ]
    }

    return obj
