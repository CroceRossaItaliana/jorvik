import json
import requests

from django.core.management import BaseCommand
from anagrafica.models import Persona
from anagrafica.serializers import PersonaSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('index', nargs='?', type=str, default=ELASTIC_CURRICULUM_INDEX)

    def handle(self, *args, **options):
        index = options['index']

        for persona in Persona.objects.all():
            s_persona = PersonaSerializer(persona)
            data = json.dumps(s_persona.data)

            url = "{}/{}/_doc".format(ELASTIC_HOST, index)
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=data)

            if response.status_code != 201:
                print(persona, response.status_code, data)
                print(response.text)
