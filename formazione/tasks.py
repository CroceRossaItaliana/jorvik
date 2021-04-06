from celery import shared_task


@shared_task(bind=True)
def task_invia_email_agli_aspiranti(self, course_pk, rispondi_a_pk):
    from anagrafica.models import Persona
    from .models import CorsoBase

    me = Persona.objects.get(pk=rispondi_a_pk)
    corso = CorsoBase.objects.get(pk=course_pk)
    corso._invia_email_agli_aspiranti(rispondi_a=me)


@shared_task(bind=True)
def task_invia_email_apertura_evento(self, evento_pk, rispondi_a_pk):
    from anagrafica.models import Persona
    from .models import Evento

    me = Persona.objects.get(pk=rispondi_a_pk)
    evento = Evento.objects.get(pk=evento_pk)
    # evento._invia_email_agli_aspiranti(rispondi_a=me)
    evento._invia_email_volotari(rispondi_a=me)
