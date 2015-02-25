"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""

from base.modelli import *
from base.tratti import *


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio):
    pass


class Destinatario(ModelloSemplice, ConMarcaTemporale):
    pass


class Allegato(ModelloSemplice, ConMarcaTemporale):
    pass