import requests


def getServiziStandard(max_result=200):
    r = requests.get(
        'https://mscriperlepersone.cri.it/service/?maxResults={}'.format(max_result)
    )
    return r.json() if r.status_code == 200 else {'services': []}
