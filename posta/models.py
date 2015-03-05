"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""

from base.models import *
from base.tratti import *
from social.models import ConGiudizio


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConAllegati):

    class Meta:
        verbose_name = "Messaggio di posta"
        verbose_name_plural = "Messaggi di posta"


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"

