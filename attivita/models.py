# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""

from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale
from base.geo import ConGeolocalizzazione


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti, ConAllegati):

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    class Meta:
        verbose_name_plural = "Turni"


class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class Area(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Aree"
