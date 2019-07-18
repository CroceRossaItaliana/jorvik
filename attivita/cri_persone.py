import requests


def getServiziStandard(max_result=200):
    r = requests.get(
        'https://mscriperlepersone.cri.it/service/?maxResults={}'.format(max_result)
    )
    return r.json() if r.status_code == 200 else {}


def createServizio(comitato, nome_progetto, servizi=[]):
    r = requests.post(
        'https://mscriperlepersone.cri.it/offeredservice',
        json={
            "committee": comitato,
            "project": nome_progetto,
            "service": servizi,
            "summary": nome_progetto
        }
    )
    return r.json() if r.status_code == 200 else {}
