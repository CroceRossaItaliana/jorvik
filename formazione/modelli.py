"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""

from base.modelli import *
from base.tratti import *


class Corso(ModelloSemplice, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio):
    pass


class Partecipazione(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):
    pass


class Lezione(ModelloSemplice, ConMarcaTemporale, ConGiudizio):
    pass


class Assenza(ModelloSemplice, ConMarcaTemporale):
    pass