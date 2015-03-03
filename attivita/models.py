# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""

from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale
from base.geo import ConGeolocalizzazione


class Attivita(ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti, ModelloSemplice):

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"


class Turno(ConMarcaTemporale, ConGiudizio, ModelloSemplice):

    class Meta:
        verbose_name_plural = "Turni"


class Partecipazione(ConMarcaTemporale, ConAutorizzazioni, ModelloSemplice):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class Area(ConMarcaTemporale, ModelloSemplice):

    class Meta:
        verbose_name_plural = "Aree"
