from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.serializers import PersonaSerializer
from anagrafica.tasks import load_elastic
from curriculum.models import TitoloPersonale
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


@receiver(post_save, sender=TitoloPersonale)
def save_titolo_personale(sender, instance, **kwargs):
    s_persona = PersonaSerializer(instance.persona)
    load_elastic.apply_async(args=(s_persona.data, ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX), task_id=uuid())
