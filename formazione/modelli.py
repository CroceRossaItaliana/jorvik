"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
from base.autorizzazioni import ConAutorizzazioni
from base.geo import ConGeolocalizzazione
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale
from social.modelli import ConCommenti, ConGiudizio


class Corso(ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio, ModelloSemplice):

    class Meta:
        verbose_name = "Corso di formazione"
        verbose_name_plural = "Corsi di formazione"


class Partecipazione(ConAutorizzazioni, ConMarcaTemporale, ModelloSemplice):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class Lezione(ConMarcaTemporale, ConGiudizio, ModelloSemplice):

    class Meta:
        verbose_name_plural = "Lezioni"


class Assenza(ConMarcaTemporale, ModelloSemplice):

    class Meta:
        verbose_name_plural = "Assenze"
