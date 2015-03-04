from django.db import models
from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Patente(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Patenti"

    CIVILE = 'CIV'
    CRI = 'CRI'
    TIPO = (
        (CIVILE, 'Patente Civile'),
        (CRI,    'Patente CRI')
    )
    tipo = models.CharField(max_length=2, choices=TIPO, default=CIVILE)


class Elemento(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Elemento patente"
        verbose_name_plural = "Elementi patente"

    # TODO tipi patente