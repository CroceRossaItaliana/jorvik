import requests
import json
from http import HTTPStatus
from celery import shared_task
from celery.utils.log import get_task_logger

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
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == HTTPStatus.CONFLICT:
        url = "{}/{}/_update/{}".format(host, index, data['id_persona'])
        response = requests.post(url, headers=headers, data=json.dumps({"doc": data}))

    if response.status_code not in [HTTPStatus.CREATED, HTTPStatus.OK]:
        logger.error('{} {}'.format(url, response.text))

    return response.status_code
