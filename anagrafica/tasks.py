import requests
import json
from celery import shared_task

@shared_task(bind=True)
def load_elastic(self, data, host, index):
    url = "{}/{}/_doc/{}?op_type=create".format(host, index, data['id'])
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))

    # return response.status_code
