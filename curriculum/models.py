from django.db import models
from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Competenza(ModelloSemplice):

    class Meta:
        verbose_name_plural = "Competenze"


class CompetenzaPersonale(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Competenza personale"
        verbose_name_plural = "Competenze personali"

    competenza = models.ForeignKey(Competenza)
    persona = models.ForeignKey("anagrafica.Persona", related_name="competenze_personali")


class Titolo(ModelloSemplice):

    class Meta:
        verbose_name_plural = "Titoli"


class TitoloPersonale(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Titolo personale"
        verbose_name_plural = "Titoli personali"

    titolo = models.ForeignKey(Titolo)
    persona = models.ForeignKey("anagrafica.Persona", related_name="titoli_personali")
