import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.models import Persona, Appartenenza
from anagrafica.serializers import PersonaSerializer
from anagrafica.tasks import load_elastic
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


@receiver(post_save, sender=Persona)
def save_persona(sender, instance, **kwargs):
    s_persona = PersonaSerializer(instance)
    data = json.dumps(s_persona.data)
    load_elastic.apply_async(args=(data, ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX), task_id=uuid())


@receiver(post_save, sender=Appartenenza)
def save_appartenenza(sender, instance, **kwargs):
    s_persona = PersonaSerializer(instance.persona)
    data = json.dumps(s_persona.data)
    load_elastic.apply_async(args=(data, ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX), task_id=uuid())
