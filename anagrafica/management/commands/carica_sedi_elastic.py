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
    DEFAULT_BATCH_SIZE = 500

    def add_arguments(self, parser):
        parser.add_argument('batch_size', nargs='?', type=int, default=self.DEFAULT_BATCH_SIZE)

    def _insert_sedi_in_elastic(self, queyset=None, batch_size=DEFAULT_BATCH_SIZE):
        count = 0

        paginator = Paginator(queyset, batch_size)

        for num_page in paginator.page_range:
            for sede in paginator.page(num_page):
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
            logger.info('** batch {} di {} completo'.format(num_page, paginator.num_pages))

        return count

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        start_time = time()

        logger.info('** Inserimento Comitati start')
        sedi = Sede.objects.all()

        count_sedi = self._insert_sedi_in_elastic(queyset=sedi, batch_size=batch_size)

        total_time = round((time() - start_time) / 60)
        total_time, tmp = (total_time, 'min') if total_time < 60 else ((total_time / 60), 'ore')

        if count_sedi == sedi.count():
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

