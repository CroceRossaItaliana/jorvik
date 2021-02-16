import json

import requests
from celery import shared_task

from anagrafica.serializers import PersonaSerializer
from formazione.serielizers import CorsoBaseSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, ELASTIC_CORSO_INDEX


def serilizer_elastic(data, index):
    url = "{}/{}/_doc".format(ELASTIC_HOST, index)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=data)

    return response.status_code


@shared_task(bind=True)
def task_volontario_elastic(self, persona):
    return serilizer_elastic(data=persona, index=ELASTIC_CURRICULUM_INDEX)


@shared_task(bind=True)
def task_corso_elastic(self, corso):
    s_corso = CorsoBaseSerializer(corso)
    return serilizer_elastic(data=json.dumps(s_corso.data), index=ELASTIC_CORSO_INDEX)
