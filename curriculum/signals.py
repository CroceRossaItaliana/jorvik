from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.tasks import task_volontario_elastic
from curriculum.models import TitoloPersonale


@receiver(post_save, sender=TitoloPersonale)
def save_titolo_personale(sender, instance, **kwargs):
    task = task_volontario_elastic.apply_async(args=(instance.persona,), task_id=uuid())
    return task
