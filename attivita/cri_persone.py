import requests


def getServiziStandard(max_result=200):
    r = requests.get(
        'https://mscriperlepersone.cri.it/service/?maxResults={}'.format(max_result)
    )
    return r.json() if r.status_code == 200 else {}


def createServizio(comitato, nome_progetto, servizi=[]):
    r = requests.post(
        'https://mscriperlepersone.cri.it/offeredservice/',
        json={
            "committee": str(comitato),
            "project": "XXX" + nome_progetto + "XXX",
            "service": servizi,
            "summary": "XXX" + nome_progetto + "XXX"
        }
    )
    resp = r.json()
    print('risposta', resp)
    return resp if 'data' in resp and resp['data'] else {}


def getServizio(key=''):
    r = requests.get(
        'https://mscriperlepersone.cri.it/offeredserviceextended/{}'.format(key)
    )
    resp = r.json()
    print('risposta', resp)
    return resp if 'data' in resp and resp['data'] else {}


def getListService(comitato):
    r = requests.get(
        'https://mscriperlepersone.cri.it/offeredservice/?committee={}'.format(comitato)
    )
    resp = r.json()
    print('risposta', resp)
    return resp if 'data' in resp and resp['data'] else {}
