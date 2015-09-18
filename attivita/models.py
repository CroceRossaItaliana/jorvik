# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""
from django.db import models

from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale, ConDelegati
from base.geo import ConGeolocalizzazione


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti,
               ConAllegati, ConDelegati):

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"

    BOZZA = 'B'
    VISIBILE = 'V'
    STATO = (
        (BOZZA, "Bozza"),
        (VISIBILE, "Visibile")
    )

    CHIUSA = 'C'
    APERTA = 'A'
    APERTURA = (
        (CHIUSA, 'Chiusa'),
        (APERTA, 'Aperta')
    )

    nome = models.CharField(max_length=255, default="Nuova attività", db_index=True)
    sede = models.ForeignKey('anagrafica.Sede', related_name='attivita')
    area = models.ForeignKey("Area", related_name='attivita')
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None, related_name='attivita_estensione')
    stato = models.CharField(choices=STATO, default=BOZZA, max_length=1, db_index=True)
    apertura = models.CharField(choices=APERTURA, default=APERTA, max_length=1, db_index=True)
    descrizione = models.TextField(blank=True)


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
