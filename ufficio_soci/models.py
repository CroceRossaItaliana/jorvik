from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Estensione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di Estensione"
        verbose_name_plural = "Richieste di Estensione"


class Trasferimento(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di Trasferimento"
        verbose_name_plural = "Richieste di Trasferimento"


class Dimissione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di Dimissione"
        verbose_name_plural = "Richieste di Dimissione"


class Tesserino(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta Tesserino Associativo"
        verbose_name_plural = "Richieste Tesserino Associativo"