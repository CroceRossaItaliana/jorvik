import logging
from time import time, sleep

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from anagrafica.models import Persona, Sede
from formazione.utils import unique_signature

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    DEFAULT_BATCH_SIZE = 500

    UUID = []

    def add_arguments(self, parser):
        parser.add_argument('batch_size', nargs='?', type=int, default=self.DEFAULT_BATCH_SIZE)

    def _update_signature(self, queyset=None, batch_size=DEFAULT_BATCH_SIZE):
        count = 0
        # paginator = Paginator(queyset, batch_size)

        # for num_page in paginator.page_range:
        #     for record in paginator.page(num_page):
        for record in queyset:
            record.signature = unique_signature(record.id, record.creazione)
            record.save()
            count += 1
            sleep(1/100)
        # logger.info('** batch {} di {} completo'.format(num_page, paginator.num_pages))

        return count

    def handle(self, *args, **options):
        batch_size = options['batch_size']

        start_time = time()
        persona_queryset = Persona.objects.filter(signature__isnull=True)
        persone_tot = persona_queryset.count()

        logger.info('** Signature Persone start count:{}'.format(persone_tot))
        count_persone = self._update_signature(queyset=persona_queryset, batch_size=batch_size)
        logger.info('** Signature Persone finish')

        sedi_queryset = Sede.objects.filter(signature__isnull=True)
        sedi_tot = sedi_queryset.count()

        logger.info('** Signature Sede start count:{}'.format(sedi_tot))
        count_sedi = self._update_signature(queyset=sedi_queryset, batch_size=batch_size)
        logger.info('** Signature Sede finish')

        if count_persone != persone_tot or count_sedi != sedi_tot:
            logger.warning(
                'Persone tot:{} update:{} - Sedi tot:{} update:{} in {} min.'.format(
                    persone_tot, count_persone, sedi_tot, count_sedi, (time() - start_time) / 60
                )
            )
        else:
            logger.info(
                'Persone tot:{} update:{} - Sedi tot:{} update:{} in {} min.'.format(
                    persone_tot, count_persone, sedi_tot, count_sedi, (time() - start_time) / 60
                )
            )

