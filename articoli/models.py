from html import unescape

from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.forms import Textarea
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField

from base.models import ModelloSemplice, ModelloAlbero, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale
from segmenti.models import BaseSegmento


class ArticoliQuerySet(models.QuerySet):
    def pubblicati(self):
        data_fine = (
            models.Q(data_fine_pubblicazione__gte=timezone.now()) |
            models.Q(data_fine_pubblicazione__isnull=True)
        )
        return self.filter(
            stato=Articolo.PUBBLICATO,
            data_inizio_pubblicazione__lte=timezone.now()
        ).filter(data_fine).prefetch_related('segmenti')

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
        (BOZZA, 'Bozza'),
        (PUBBLICATO, 'Pubblicato')
    )
    DIMENSIONE_ESTRATTO = 1014

    titolo = models.CharField('Titolo', max_length=255, db_index=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    corpo = RichTextField('Corpo')
    estratto = models.CharField('Estratto', max_length=1024, blank=True, null=True)
    data_inizio_pubblicazione = models.DateTimeField('Data di inizio pubblicazione', default=timezone.now, db_index=True)
    data_fine_pubblicazione = models.DateTimeField('Data di fine pubblicazione', db_index=True, blank=True, null=True)
    visualizzazioni = models.PositiveIntegerField('Visualizzazioni', db_index=True, default=0)
    stato = models.CharField('Stato', max_length=1, choices=STATO, default=BOZZA, db_index=True)

    objects = ArticoliManager()

    def __str__(self):
        return self.titolo

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titolo)
        if not self.estratto:
            corpo = self.corpo
        else:
            corpo = self.estratto
        self.estratto = unescape(strip_tags(corpo))[:self.DIMENSIONE_ESTRATTO]
        super(Articolo, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('dettaglio_articolo', kwargs={'articolo_slug': self.slug})

    class Meta:
        app_label = 'articoli'
        ordering = ['-data_inizio_pubblicazione']
        verbose_name = 'articolo'
        verbose_name_plural = 'articoli'
        permissions = (
            ("view_articolo", "Can view articolo"),
        )

    @property
    def pubblicato(self):
        return self.stato == self.PUBBLICATO

    @property
    def termina(self):
        return self.data_fine_pubblicazione is not None

    @property
    def segmenti_testo(self):
        """
        Ritorna una descrizione dei segmenti applicati in testo (inline)
        """
        if self.segmenti.exists():
            segmenti = self.segmenti.all()
            return ", ".join([str(x) for x in segmenti])
        return "Pubblico (nessun segmento)"

    @transaction.atomic
    def incrementa_visualizzazioni(self):
        self.visualizzazioni += 1
        self.save()


class ArticoloSegmento(BaseSegmento):
    _oggetto_collegato = Articolo

    class Meta:
        verbose_name = "Articolo Segmento"
        verbose_name_plural = "Articolo Segmenti"
        permissions = (
            ("view_articolosegmento", "Can view articolo segmento"),
        )       
