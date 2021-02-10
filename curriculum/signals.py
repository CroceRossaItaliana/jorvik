from django.db.models.signals import post_save
from django.dispatch import receiver

from curriculum.models import TitoloPersonale


@receiver(post_save, sender=TitoloPersonale)
def foo(sender, instance, **kwargs):
    print('segnale', instance)
