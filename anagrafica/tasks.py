import json

import requests
from celery import shared_task

from anagrafica.serializers import PersonaSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


@shared_task(bind=True)
def task_volontario_elastic(self, persona):
    s_persona = PersonaSerializer(persona)
    data = json.dumps(s_persona.data)
    url = "{}/{}/_doc".format(ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=data)

    return response.status_code


@shared_task(bind=True)
def task_corso_elastic(self, corso):
    pass
