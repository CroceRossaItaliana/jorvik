import json
import logging
from http import HTTPStatus
from time import sleep, time

import requests

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from anagrafica.models import Sede
from anagrafica.serializers import ComitatoSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_COMITATO_INDEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def _insert_sedi_in_elastic(self, queyset=None):
        count = 0

        for sede in queyset:
            s_sede = ComitatoSerializer(sede)
            data = s_sede.data

            url = "{}/{}/_doc/{}?op_type=create".format(ELASTIC_HOST, ELASTIC_COMITATO_INDEX, data['id_comitato'])
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.put(url, headers=headers, data=json.dumps(data))
            if response.status_code == HTTPStatus.CREATED:
                count += 1
            else:
                logger.warning('{} {}'.format(url, response.status_code))

        return count

    def handle(self, *args, **options):
        start_time = time()

        logger.info('** Inserimento Comitati start')
        sedi = Sede.objects.all()

        count_sedi = self._insert_sedi_in_elastic(queyset=sedi)

        if count_sedi == sedi.count():
            logger.info('Sedi {} caricate {} Completato in {} min.'.format(sedi.count(), count_sedi, (time() - start_time) / 60))
        else:
            logger.warning('Sedi {} caricate {} Completato in {} min.'.format(sedi.count(), count_sedi, (time() - start_time) / 60))

