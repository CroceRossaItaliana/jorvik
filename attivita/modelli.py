"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""

from base.modelli import *
from base.tratti import *


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti):

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

