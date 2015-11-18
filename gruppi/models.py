from django.db import models
from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale, ConEstensione

__author__ = 'alfioemanuele'


class Gruppo(ModelloSemplice, ConEstensione, ConMarcaTemporale):
    nome = models.CharField("Nome", max_length=127)

    class Meta:
        verbose_name_plural = "Gruppi"


class Appartenenza(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Appartenenze"

