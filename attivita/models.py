# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""
from django.db import models

from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale, ConDelegati
from base.geo import ConGeolocalizzazione


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti, ConAllegati):

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"

    sede = models.ForeignKey('anagrafica.Sede', related_name='attivita')
    area = models.ForeignKey("Area", related_name='attivita')


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    class Meta:
        verbose_name_plural = "Turni"

    attivita = models.ForeignKey(Attivita, related_name='turni')



class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"

    persona = models.ForeignKey("anagrafica.Persona", related_name='partecipazioni')
    turno = models.ForeignKey(Turno, related_name='partecipazioni')


class Area(ModelloSemplice, ConMarcaTemporale, ConDelegati):

    sede = models.ForeignKey('anagrafica.Sede', related_name='aree')
    nome = models.CharField(max_length=256, db_index=True, default='Generale', blank=False)
    obiettivo = models.SmallIntegerField(null=False, blank=False, default=1, db_index=True)

    class Meta:
        verbose_name_plural = "Aree"
