import requests
from celery import shared_task

from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, ELASTIC_CORSO_INDEX


@shared_task(bind=True)
def task_volontario_elastic(self, persona):
    url = "{}/{}/_doc".format(ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=persona)

    return response.status_code


@shared_task(bind=True)
def task_corso_elastic(self, corso):
    url = "{}/{}/_doc".format(ELASTIC_HOST, ELASTIC_CORSO_INDEX)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=corso)

    return response.status_code
