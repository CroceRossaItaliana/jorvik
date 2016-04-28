from django.db import models

from articoli.models import Articolo


class ArticoliQuerySet(models.QuerySet):
    def pubblicati(self):
        return self.filter(stato=Articolo.PUBBLICATO)

    def bozze(self):
        return self.filter(stato=Articolo.BOZZA)


class ArticoliManager(models.Manager):
    def get_queryset(self):
        return ArticoliQuerySet(self.model, using=self._db)

    def pubblicati(self):
        return self.get_queryset().pubblicati()

    def bozze(self):
        return self.get_queryset().bozze()
