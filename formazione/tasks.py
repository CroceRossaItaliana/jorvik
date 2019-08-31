from celery import shared_task


@shared_task(bind=True)
def task_invia_email_agli_aspiranti(self, course_pk, rispondi_a_pk):
    from anagrafica.models import Persona
    from .models import CorsoBase

    me = Persona.objects.get(pk=rispondi_a_pk)
    corso = CorsoBase.objects.get(pk=course_pk)
    corso._invia_email_agli_aspiranti(rispondi_a=me)
