import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.models import Persona, Appartenenza
from anagrafica.serializers import PersonaSerializer
from anagrafica.tasks import task_volontario_elastic, serilizer_elastic
from jorvik.settings import ELASTIC_CURRICULUM_INDEX


@receiver(post_save, sender=Persona)
def save_persona(sender, instance, **kwargs):
    s_persona = PersonaSerializer(instance)
    return task_volontario_elastic.apply_async(args=(json.dumps(s_persona.data),), task_id=uuid())


@receiver(post_save, sender=Appartenenza)
def save_appartenenza(sender, instance, **kwargs):
    return task_volontario_elastic.apply_async(args=(instance.persona,), task_id=uuid())
