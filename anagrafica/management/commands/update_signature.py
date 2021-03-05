import logging
import uuid
from time import sleep

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from anagrafica.models import Persona, Sede

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    DEFAULT_BATCH_SIZE = 200

    def add_arguments(self, parser):
        parser.add_argument('batch_size', nargs='?', type=int, default=self.DEFAULT_BATCH_SIZE)

    def _update_signature(self, queyset=None, batch_size=DEFAULT_BATCH_SIZE):
        count = 0

        persone_paginator = Paginator(queyset, batch_size)

        for num_page in persone_paginator.page_range:
            for persona in persone_paginator.page(num_page):
                persona.signature = uuid.uuid4()
                persona.save()
                count += 1
            sleep(30)

        return count

    def handle(self, *args, **options):
        batch_size = options['batch_size']

        persona_queryset = Persona.objects.all()
        logger.info('** Signature Persone start')
        count_persone = self._update_signature(queyset=persona_queryset, batch_size=batch_size)
        logger.info('** Signature Persone finish')

        sedi_queryset = Sede.objects.all()
        logger.info('** Signature Sede start')
        count_sedi = self._update_signature(queyset=sedi_queryset, batch_size=batch_size)
        logger.info('** Signature Sede finish')

        persone_tot = persona_queryset.count()
        sedi_tot = sedi_queryset.count()

        if count_persone != persone_tot or count_sedi != sedi_tot:
            logger.warning(
                'Persone tot:{} inserite:{} - Sedi tot:{} inserite:{}'.format(
                    persone_tot, count_persone, sedi_tot, count_sedi
                )
            )
        else:
            logger.info(
                'Persone tot:{} inserite:{} - Sedi tot:{} inserite:{}'.format(
                    persone_tot, count_persone, sedi_tot, count_sedi
                )
            )

