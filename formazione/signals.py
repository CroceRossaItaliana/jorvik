import json
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from formazione.models import CorsoBase
from formazione.serielizers import CorsoBaseSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CORSO_INDEX
from anagrafica.tasks import load_elastic


@receiver(post_save, sender=CorsoBase)
def save_corso_base(sender, instance, **kwargs):
    corso = CorsoBaseSerializer(instance)
    load_elastic.apply_async(args=(json.dumps(corso.data), ELASTIC_HOST, ELASTIC_CORSO_INDEX), task_id=uuid.uuid4())
