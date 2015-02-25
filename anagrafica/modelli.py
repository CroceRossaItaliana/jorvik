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
    pass


class Telefono(ModelloSemplice, ConMarcaTemporale):
    pass


class Documento(ModelloSemplice, ConMarcaTemporale):
    pass


class Utente(ModelloSemplice):
    pass


class Appartenenza(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):
    pass


class Comitato(ModelloAlbero, ConGeolocalizzazione):
    pass


class Delega(ModelloSemplice, ConMarcaTemporale):
    pass