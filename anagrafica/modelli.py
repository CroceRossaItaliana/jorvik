"""
Questo modulo definisce i modelli del modulo anagrafico di Gaia.

- Persona
- Telefono
- Documento
- Utente
- Appartenenza
- Comitato
- Delega
"""

from base.modelli import *
from base.tratti import *


class Persona(ModelloCancellabile, ConGeolocalizzazioneRaggio):

    class Meta:
        verbose_name_plural = "Persone"


class Telefono(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Numero di telefono"
        verbose_name_plural = "Numeri di telefono"


class Documento(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Documenti"


class Utenza(ModelloSemplice):

    class Meta:
        verbose_name_plural = "Utenze"


class Appartenenza(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name_plural = "Appartenenze"


class Comitato(ModelloAlbero, ConGeolocalizzazione):

    class Meta:
        verbose_name_plural = "Comitati"


class Delega(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Deleghe"
