import json

from celery import shared_task

from anagrafica.serializers import PersonaSerializer


@shared_task(bind=True)
def task_volontario_elastic(self, persona):
    s_persona = PersonaSerializer(persona)
    data = json.dumps(s_persona.data)
    # TODO: ELASTIC request


@shared_task(bind=True)
def task_corso_elastic(self, corso):
    pass
