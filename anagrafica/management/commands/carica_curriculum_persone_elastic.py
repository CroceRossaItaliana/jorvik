import json
import logging
from http import HTTPStatus
from time import sleep, time

import requests

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from anagrafica.models import Persona
from anagrafica.serializers import CurriculumPersonaSerializer, PersonaSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, ELASTIC_PERSONA_INDEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def _check_insert(self, url, response):
        if response.status_code == HTTPStatus.CREATED:
            return 1
        else:
            logger.warning('{} {} {}'.format(url, response.status_code, response.text))
            return 0

    def _insert_curriculum_persone_elastic(self, queyset=None):

        count_curriculum = 0
        count_persone = 0

        for persona in queyset:
            s_curriculum = CurriculumPersonaSerializer(persona)
            data = s_curriculum.data
            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, data['id_persona'])
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.put(url, headers=headers, data=json.dumps(data))

            count_curriculum += self._check_insert(url=url, response=response)

            s_persona = PersonaSerializer(persona)
            data = s_persona.data
            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, ELASTIC_PERSONA_INDEX, data['id_persona'])

            response = requests.put(url, headers=headers, data=json.dumps(data))

            count_persone += self._check_insert(url=url, response=response)

        return count_curriculum, count_persone

    def handle(self, *args, **options):
        start_time = time()

        logger.info('** Inserimento Persone/Curriculum start')
        persone_queryset = Persona.objects.all()

        curriculum, persone = self._insert_curriculum_persone_elastic(queyset=persone_queryset)

        tot_persone = persone_queryset.count()

        if curriculum != tot_persone or persone != tot_persone:
            logger.warning('Curriculum {} caricati {}'.format(tot_persone, curriculum))
            logger.warning('Persone {} caricati {}'.format(tot_persone, curriculum))
        else:
            logger.info('Curriculum {} caricati {}'.format(tot_persone, curriculum))
            logger.info('Persone {} caricati {}'.format(tot_persone, curriculum))

        logger.info('Completato in {} min.'.format((time() - start_time) / 60))
