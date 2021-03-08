import logging
import uuid
from time import time

from django.core.management import BaseCommand

from anagrafica.models import Persona, Sede

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def _update_signature(self, queyset=None):
        count = 0
        for record in queyset:
            record.signature = uuid.uuid4()
            record.save()
            count += 1

        return count

    def handle(self, *args, **options):
        start_time = time()
        persona_queryset = Persona.objects.all()
        logger.info('** Signature Persone start')
        count_persone = self._update_signature(queyset=persona_queryset)
        logger.info('** Signature Persone finish')

        sedi_queryset = Sede.objects.all()
        logger.info('** Signature Sede start')
        count_sedi = self._update_signature(queyset=sedi_queryset)
        logger.info('** Signature Sede finish')

        persone_tot = persona_queryset.count()
        sedi_tot = sedi_queryset.count()

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

