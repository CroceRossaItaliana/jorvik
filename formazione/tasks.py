from celery import shared_task

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def task_invia_email_agli_aspiranti(self, course_pk, rispondi_a_pk):
    from anagrafica.models import Persona
    from .models import CorsoBase
    me = Persona.objects.get(pk=rispondi_a_pk)
    corso = CorsoBase.objects.get(pk=course_pk)
    logger.info("me: {} corso: {}".format(me, corso))
    corso._invia_email_agli_aspiranti(rispondi_a=me)


@shared_task(bind=True)
def task_invia_email_apertura_evento(self, evento_pk, rispondi_a_pk):
    from anagrafica.models import Persona
    from .models import Evento

    me = Persona.objects.get(pk=rispondi_a_pk)
    evento = Evento.objects.get(pk=evento_pk)
    evento._invia_email_volotari(rispondi_a=me)
