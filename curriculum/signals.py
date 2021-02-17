import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.serializers import PersonaSerializer
from anagrafica.tasks import task_volontario_elastic
from curriculum.models import TitoloPersonale


@receiver(post_save, sender=TitoloPersonale)
def save_titolo_personale(sender, instance, **kwargs):
    s_persona = PersonaSerializer(instance.persona)
    task_volontario_elastic.apply_async(args=(json.dumps(s_persona.data),), task_id=uuid())
