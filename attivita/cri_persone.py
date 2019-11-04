import requests
from django.conf import settings
import logging

end_point = settings.APIS_CONF['crip']['endpoint']
am_end_pont = settings.APIS_CONF['crip']['am_end_pont']

logger = logging.getLogger(__name__)

def getServiziStandard(max_result=200):
    r = requests.get(
        '{}/service/?maxResults={}'.format(end_point, max_result)
    )
    return r.json() if r.status_code == 200 else {}


def getBeneficiary():
    r = requests.get(
        '{}/public/cri/crip/autosug/offeredservice/beneficiarytype'.format(am_end_pont)
    )
    return r.json() if r.status_code == 200 else {}


def getPrevisioning():
    r = requests.get(
        '{}/generic_issue/CRIP-Provision'.format(end_point)
    )
    return r.json() if r.status_code == 200 else {}


def updateServizio(key, **kwargs):
    data = {}
    if kwargs.get('referenti'):
        data['accountables'] = [{'name': '{}.{}'.format(
            ref.nome.lower(), ref.cognome.lower()
        )} for ref in kwargs.get('referenti')]
        logger.debug('- referenti {}'.format(kwargs.get('referenti')))

    if kwargs.get('precedenti'):
        l = []
        for ref in kwargs.get('precedenti'):
            l.append({'name': ref})
        if 'accountables' in data:
            data['accountables'].extend(l)
        else:
            data['accountables'] = l
        logger.debug('- precedenti {}'.format(kwargs.get('precedenti')))

    if kwargs.get('servizi'):
        ss = ""
        for s in kwargs.get('servizi'):
            ss += "{},".format(s)
        data['service'] = [ss[:-1] if ss else ""]

    if kwargs.get('testo'):
        data['description'] = kwargs.get('testo')

    if kwargs.get('address'):
        data['address'] = kwargs.get('address')

    r = requests.put(
        '{}/offeredserviceextended/{}/'.format(end_point, key),
        json=data
    )
    resp = r.json()
    logger.debug('- updateServizio {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}


def update_service(key, **kwargs):

    r = requests.put(
        '{}/offeredserviceextended/{}/'.format(end_point, key),
        json=kwargs
    )

    resp = r.json()
    logger.debug('- _updateServizio {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}

def changeState(key='', state=''):

    STATE_TO_CODE = {
        "11301": "11",
        "10413": "31",
        "6": "21"
    }

    r = requests.post(
        '{}/offeredservice/{}/transition/{}/'.format(end_point, key, STATE_TO_CODE[state])
    )
    resp = r.json()
    logger.debug('- changeState {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}


def createServizio(comitato, nome_progetto, servizi=[]):
    ss = ""
    for s in servizi:
        ss += "{},".format(s)

    data = {
        "committee": str(comitato),
        "project": "XXX" + nome_progetto + "XXX",
        "service": [ss[:-1]],
        "summary": "XXX" + nome_progetto + "XXX"
    }

    r = requests.post(
        '{}/offeredservice/'.format(end_point),
        json=data
    )
    resp = r.json()
    logger.debug('- createServizio {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'data' in resp and resp['data'] else {}


def getServizio(key=''):
    r = requests.get(
        '{}/offeredserviceextended/{}'.format(end_point, key)
    )
    resp = r.json()
    logger.debug('- getServizio {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'data' in resp and resp['data'] else {}


def getListService(comitato):
    r = requests.get(
        '{}/offeredservice/?committee={}'.format(end_point, comitato)
    )
    resp = r.json()
    logger.debug('- getListService {} {} {}'.format(r.url, resp['result']['code'], resp['result']['description']))
    return resp if 'data' in resp and resp['data'] else {}


def deleteService(key=''):
    r = requests.delete(
        '{}/offeredservice/{}'.format(end_point, key)
    )
    resp = r.json()
    logger.debug('- deleteService {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}


def createStagilTurni(giorni=[], apertura='', chiusura='', id=0):
    data = {
        "giorno": giorni,
        "orario_apertura": apertura,
        "orario_chiusura": chiusura,
        "customFieldId": "11723",
        "issueId": id
    }

    r = requests.post(
        '{}/stagiltables/'.format(end_point),
        json=data
    )
    resp = r.json()
    logger.debug('- createStagilTurni {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'data' in resp and resp['data'] else {}

def deleteStagil(id=0):
    r = requests.delete(
        '{}/stagiltables/{}/'.format(end_point, id)
    )
    resp = r.json()
    logger.debug('- deleteStagil {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}


def createStagilContatti(tipo_contatto='', nome='', telefono='', email='', id=0):
    data = {
        "tipo_contatto": [str(tipo_contatto)],
        "nome": nome,
        "telefono": telefono,
        "email": email,
        "customFieldId": "11857",
        "issueId": id
    }

    r = requests.post(
        '{}/stagiltables/'.format(end_point),
        json=data
    )
    resp = r.json()
    logger.debug('- createStagilContatti {} {}'.format(resp['result']['code'], resp['result']['description']))
    return resp if 'data' in resp and resp['data'] else {}
