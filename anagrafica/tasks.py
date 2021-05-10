import requests
import json
from http import HTTPStatus
from celery import shared_task
from celery.utils.log import get_task_logger
from requests.auth import HTTPBasicAuth

from jorvik import settings

logger = get_task_logger(__name__)


@shared_task(bind=True)
def load_elastic(self, data, host, index):
    if 'id_persona' in data:
        url = "{}/{}/_doc/{}?op_type=create".format(host, index, data['id_persona'])
    elif 'id_comitato' in data:
        url = "{}/{}/_doc/{}?op_type=create".format(host, index, data['id_comitato'])
    else:
        return 'id not found'

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.put(url, headers=headers, data=json.dumps(data), auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD))
    if response.status_code == HTTPStatus.CONFLICT:
        if 'id_persona' in data:
            url = "{}/{}/_update/{}".format(host, index, data['id_persona'])
        elif 'id_comitato' in data:
            url = "{}/{}/_update/{}".format(host, index, data['id_comitato'])
        else:
            return 'id not found'

        response = requests.post(url, headers=headers, data=json.dumps({"doc": data}), auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD))

    if response.status_code not in [HTTPStatus.CREATED, HTTPStatus.OK]:
        logger.error('{} {}'.format(url, response.text))

    return response.status_code


@shared_task(bind=True)
def delete_elastic(self, host, index, id):
    url = "{}/{}/_doc/{}".format(host, index, id)

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.delete(url, headers=headers, auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD))

    if response.status_code != HTTPStatus.OK:
        logger.error('{} {}'.format(url, response.text))

    return response.status_code
