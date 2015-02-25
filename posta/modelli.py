"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""

from base.modelli import *
from base.tratti import *


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    class Meta:
        verbose_name = "Messaggio di posta"
        verbose_name_plural = "Messaggi di posta"


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"


class Allegato(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Allegati"
