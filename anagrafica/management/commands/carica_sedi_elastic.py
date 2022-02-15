import json
import logging
from http import HTTPStatus
from time import sleep, time

import requests

from django.core.management import BaseCommand
from django.core.paginator import Paginator
from requests.auth import HTTPBasicAuth

from anagrafica.models import Sede
from anagrafica.serializers import ComitatoSerializer
from jorvik import settings
from jorvik.settings import ELASTIC_HOST, ELASTIC_COMITATO_INDEX

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # DEFAULT_BATCH_SIZE = 500
    #
    # def add_arguments(self, parser):
    #     parser.add_argument('batch_size', nargs='?', type=int, default=self.DEFAULT_BATCH_SIZE)

    def _insert_sedi_in_elastic(self, queyset=None):
        count_sedi = 0

        for sede in queyset:
            s_sede = ComitatoSerializer(sede)
            data = s_sede.data

            url = "{}/{}/_doc/{}".format(ELASTIC_HOST, ELASTIC_COMITATO_INDEX, data['id_comitato'])
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.put(url, headers=headers, data=json.dumps(data),
                                    auth=HTTPBasicAuth(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
                                    verify=False)
            if response.status_code == HTTPStatus.CREATED:
                count_sedi += 1
            else:
                logger.warning('{} {}'.format(url, response.status_code))

        return count_sedi

    def handle(self, *args, **options):
        start_time = time()

        sedi = Sede.objects.filter(signature__isnull=False)
        count = sedi.count()
        logger.info('** Inserimento Comitati start count:{}'.format(count))

        count_sedi = self._insert_sedi_in_elastic(queyset=sedi)

        total_time = round((time() - start_time) / 60)
        total_time, tmp = (total_time, 'min') if total_time < 60 else ((total_time / 60), 'ore')

        if count_sedi == count:
            logger.info(
                'Sedi {} caricate {} Completato in {} {}.'.format(
                    sedi.count(), count_sedi, total_time, tmp
                )
            )
        else:
            logger.warning('Sedi {} caricate {} Completato in {} {}.'.format(
                sedi.count(), count_sedi, total_time, tmp
                )
            )

