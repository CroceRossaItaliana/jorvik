from base.models import ModelloSemplice
from base.tratti import ConEstensione, ConStorico
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Autoparco(ModelloSemplice, ConEstensione, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Autoparchi"


class Veicolo(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Veicoli"


class Collocazione(ModelloSemplice, ConStorico):

    class Meta:
        verbose_name = "Collocazione veicolo"
        verbose_name_plural = "Collocazioni veicolo"


class FermoTecnico(ModelloSemplice, ConStorico, ConMarcaTemporale):

    class Meta:
        verbose_name = "Fermo tecnico"
        verbose_name_plural = "Fermi tecnici"


class Manutenzione(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Manutenzioni"
