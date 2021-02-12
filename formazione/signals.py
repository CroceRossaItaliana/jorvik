import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from formazione.models import CorsoBase
from anagrafica.tasks import task_corso_elastic


@receiver(post_save, sender=CorsoBase)
def save_corso_base(sender, instance, **kwargs):
    task = task_corso_elastic.apply_async(args=(instance,), task_id=uuid.uuid4())
    return task
