from celery import shared_task
from celery.utils.log import get_task_logger

from anagrafica.models import Persona
from django.core.cache import cache
from ufficio_soci.viste import prepare_us

logger = get_task_logger(__name__)


@shared_task(bind=True)
def prefetch_onlogin(self, pk):

    persona = Persona.objects.get(pk=pk)
    us_data = prepare_us(persona)

    cache.set('{}_us_sedi'.format(pk), [s.id for s in us_data.get('sedi')])
    cache.set('{}_us_persone'.format(pk), us_data.get('persone'))
    cache.set('{}_us_attivi'.format(pk), us_data.get('attivi'))

    print(cache.get('{}_us_sedi'.format(pk)))
