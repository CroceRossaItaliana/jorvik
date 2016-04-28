from django.db import models
from django.utils import timezone

from ckeditor.fields import RichTextField

from base.models import ModelloSemplice, ModelloAlbero, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale
from segmenti.models import BaseSegmento


class Articolo(ModelloSemplice, ConMarcaTemporale, ConAllegati):
    """
    Rappresenta un articolo (news).
    """

    BOZZA = 'B'
    PUBBLICATO = 'P'
    STATO = (
        (BOZZA, "Bozza"),
        (PUBBLICATO, "Pubblicato")
    )

    titolo = models.CharField("Titolo", max_length=255, db_index=True)
    corpo = RichTextField("Corpo")
    estratto = models.CharField("Estratto", max_length=1024, blank=True, null=True)
    data_inizio_pubblicazione = models.DateTimeField("Data di inizio pubblicazione", default=timezone.now, db_index=True)
    data_fine_pubblicazione = models.DateTimeField("Data di fine pubblicazione", db_index=True, blank=True, null=True)
    visualizzazioni = models.PositiveIntegerField("Visualizzazioni", db_index=True, default=0)
    stato = models.CharField("Stato", max_length=1, choices=STATO, default=BOZZA, db_index=True)
    autore = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="articoli", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name_plural = "Articoli"
        app_label = 'articoli'
        ordering = ['-data_inizio_pubblicazione']

    @property
    def pubblicato(self):
        return self.stato == self.PUBBLICATO

    @property
    def termina(self):
        return self.data_fine_pubblicazione is not None


class ArticoloSegmento(BaseSegmento):
    articolo = models.ForeignKey(Articolo, related_name="segmenti")

    class Meta:
        verbose_name_plural = "Segmenti dell'Articolo"
        app_label = 'articoli'
