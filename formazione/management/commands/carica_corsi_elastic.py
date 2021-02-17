import json
import requests
from django.core.management import BaseCommand
from formazione.serielizers import CorsoBaseSerializer
from formazione.models import CorsoBase
from jorvik.settings import ELASTIC_HOST, ELASTIC_CORSO_INDEX


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('index', nargs='?', type=str, default=ELASTIC_CORSO_INDEX)

    def handle(self, *args, **options):
        index = options['index']
        print('** {}'.format(index))
        for corso in CorsoBase.objects.all():
            s_corso = CorsoBaseSerializer(corso)
            data = s_corso.data
            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, index, data['id'])
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code != 201:
                print(corso, response.status_code, data)
                print(response.text)
            break
