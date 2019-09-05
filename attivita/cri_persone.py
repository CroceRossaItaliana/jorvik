import requests
from django.conf import settings

end_point = settings.APIS_CONF['crip']['endpoint']
import logging

logger = logging.getLogger(__name__)

def getServiziStandard(max_result=200):
    r = requests.get(
        '{}/service/?maxResults={}'.format(end_point, max_result)
    )
    return r.json() if r.status_code == 200 else {}


def updateServizio(key, **kwargs):
    data = {}
    if kwargs.get('referenti'):
        data['accountables'] = [{'name': '{}.{}'.format(ref.nome, ref.cognome)} for ref in kwargs.get('referenti')]
        logger.debug(data['accountables'])

    if kwargs.get('precedenti'):
        data['accountables'].extend(kwargs.get('precedenti'))

    if kwargs.get('servizi'):
        ss = ""
        for s in kwargs.get('servizi'):
            ss += "{},".format(s)
        data['service'] = [ss[:-1] if ss else ""]

    if kwargs.get('testo'):
        data['description'] = kwargs.get('testo')

    r = requests.put(
        '{}/offeredserviceextended/{}/'.format(end_point, key),
        json=data
    )
    resp = r.json()
    print('update', resp)
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
    print('change state', resp)
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
    print('create', resp)
    return resp if 'data' in resp and resp['data'] else {}


def getServizio(key=''):
    r = requests.get(
        '{}/offeredserviceextended/{}'.format(end_point, key)
    )
    resp = r.json()
    print('get', resp)
    return resp if 'data' in resp and resp['data'] else {}


def getListService(comitato):
    r = requests.get(
        '{}/offeredservice/?committee={}'.format(end_point, comitato)
    )
    resp = r.json()
    print('list', resp)
    return resp if 'data' in resp and resp['data'] else {}


def deleteService(key=''):
    r = requests.delete(
        '{}/offeredservice/{}'.format(end_point, key)
    )
    resp = r.json()
    print('delete', resp)
    return resp if 'result' in resp and resp['result']['code'] == 204 else {}