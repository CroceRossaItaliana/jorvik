import json
import logging

import requests

from django.core.management import BaseCommand
from anagrafica.models import Persona
from anagrafica.serializers import CurriculumPersonaSerializer, PersonaSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, ELASTIC_PERSONA_INDEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def _check(self, count=0, response=None, persona=None, url=None):
        if response.status_code != 201:
            logger.warning('{} {} {} - {}'.format(persona, url, response.text, response.status_code))
            return count
        else:
            logger.info('{} {} - {}'.format(persona, url, response.status_code))
            return count + 1

    def handle(self, *args, **options):
        count_persone = 0
        count_curriculum = 0
        for persona in Persona.objects.all():
            s_curriculum = CurriculumPersonaSerializer(persona)
            data = s_curriculum.data
            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, data['id_persona'])
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.put(url, headers=headers, data=json.dumps(data))

            count_persone = self._check(count=count_persone, response=response, persona=persona, url=url)

            s_persona = PersonaSerializer(persona)
            data = s_persona.data
            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, ELASTIC_PERSONA_INDEX, data['id_persona'])

            response = requests.put(url, headers=headers, data=json.dumps(data))

            count_curriculum = self._check(count=count_curriculum, response=response, persona=persona, url=url)

        print('Persone caricate {}'.format(count_persone))
        print('Curriculum caricati {}'.format(count_curriculum))
