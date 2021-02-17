import requests
from celery import shared_task


@shared_task(bind=True)
def load_elastic(self, data, host, index):
    url = "{}/{}/_doc".format(host, index)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=data)

    return response.status_code
