"""
Questo modulo e' una collezione di Tratti.

I tratti possono essere aggiunti ai modelli per aggiugere
dei set di funzionalita'. Si noti bene che ogni tratto
potrebbe necessitare l'implementazione di metodi o proprieta'
particolari. Fare riferimento alla documentazione del tratto
utilizzato.
"""
from base.models import ModelloSemplice
from django.db import models


class ConMarcaTemporale(ModelloSemplice):
    """
    Aggiunge le marche temporali automatiche di creazione ed ultima modifica.
    """

    class Meta:
        abstract = True

    creazione = models.DateTimeField(auto_now_add=True, db_index=True)
    ultima_modifica = models.DateTimeField(auto_now=True, db_index=True)

