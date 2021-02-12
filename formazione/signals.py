from django.db.models.signals import post_save
from django.dispatch import receiver
from kombu import uuid

from anagrafica.tasks import task_volontario_elastic
from formazione.models import CorsoBase


@receiver(post_save, sender=CorsoBase)
def save_corso_base(sender, instance, **kwargs):
    pass
    # task = task_volontario_elastic.apply_async(args=(instance.persona,), task_id=uuid())
    # return task
