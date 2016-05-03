from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField

from base.models import ModelloSemplice, ModelloAlbero, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale
from segmenti.models import BaseSegmento


class ArticoliQuerySet(models.QuerySet):
    def pubblicati(self):
        return self.filter(stato=Articolo.PUBBLICATO).prefetch_related('segmenti')

    def bozze(self):
        return self.filter(stato=Articolo.BOZZA).prefetch_related('segmenti')


class ArticoliManager(models.Manager):
    def get_queryset(self):
        return ArticoliQuerySet(self.model, using=self._db)

    def pubblicati(self):
        return self.get_queryset().pubblicati()

    def bozze(self):
        return self.get_queryset().bozze()


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
    slug = models.SlugField(unique=True, blank=True, null=True)
    corpo = RichTextField("Corpo")
    estratto = models.CharField("Estratto", max_length=1024, blank=True, null=True)
    data_inizio_pubblicazione = models.DateTimeField("Data di inizio pubblicazione", default=timezone.now, db_index=True)
    data_fine_pubblicazione = models.DateTimeField("Data di fine pubblicazione", db_index=True, blank=True, null=True)
    visualizzazioni = models.PositiveIntegerField("Visualizzazioni", db_index=True, default=0)
    stato = models.CharField("Stato", max_length=1, choices=STATO, default=BOZZA, db_index=True)

    objects = ArticoliManager()

    def __str__(self):
        return self.titolo

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titolo)
        corpo = strip_tags(self.corpo)
        if not self.estratto:
            self.estratto = corpo[:1024]
        super(Articolo, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('dettaglio_articolo', kwargs={'articolo_slug': self.slug})

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

    @transaction.atomic
    def incrementa_visualizzazioni(self):
        self.visualizzazioni += 1
        self.save()


class ArticoloSegmento(BaseSegmento):
    articolo = models.ForeignKey(Articolo, related_name="segmenti")

    class Meta:
        verbose_name_plural = "Segmenti dell'Articolo"
        app_label = 'articoli'
