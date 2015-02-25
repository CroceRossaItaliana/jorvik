"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""

from base.modelli import *
from base.tratti import *


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti):
    pass


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):
    pass


class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):
    pass

