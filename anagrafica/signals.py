from django.db.models.signals import post_save
from django.dispatch import receiver

from anagrafica.models import Persona, Appartenenza
from base.elasticsearch_function import serializer_persona


@receiver(post_save, sender=Persona)
def save_persona(sender, instance, **kwargs):
    serializer_persona(instance.id)


@receiver(post_save, sender=Appartenenza)
def save_appartenenza(sender, instance, **kwargs):
    print('save_appartenenza', instance)
