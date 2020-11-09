# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from filer.models import File
from filer.models.abstract import BaseImage

from anagrafica.validators import valida_dimensione_file_8mb
from base.models import ModelloSemplice
from base.stringhe import GeneratoreNomeFile
from base.tratti import ConMarcaTemporale
from segmenti.models import BaseSegmento


class InterfacciaJorvik(object):

    @property
    def url(self):
        """
        Mappa la proprietà di filer gestendo il nuovo campo
        """
        if self.url_documento:
            return self.url_documento
        return super(InterfacciaJorvik, self).url

    @property
    def path(self):
        """
        Mappa la proprietà di filer gestendo il nuovo campo
        """
        if self.url_documento:
            return self.url_documento
        return super(InterfacciaJorvik, self).path

    @transaction.atomic
    def incrementa_downloads(self):
        self.downloads += 1
        self.save()

    @property
    def url_scarica(self):
        return reverse('documenti:scarica_file', args=(self.pk,))

    def lista_segmenti(self):
        return ', '.join([force_text(segmento) for segmento in self.segmenti.all()])


class Documento(InterfacciaJorvik, File):
    url_documento = models.URLField(_('URL Documento'), default='', blank=True)
    downloads = models.PositiveIntegerField('Downloads', db_index=True, default=0)
    data_pubblicazione = models.DateTimeField(_('Data pubblicazione'), default=now)

    class Meta:
        abstract = False
        app_label = 'gestione_file'
        verbose_name = 'documento'
        verbose_name_plural = 'documenti'

    def icona(self):
        if self.url_documento:
            return 'fa fa-external-link-square'
        else:
            return 'fa fa-file-code-o'


class DocumentoComitato(ModelloSemplice, ConMarcaTemporale):

    nome = models.CharField(max_length=150, db_index=True)
    file = models.FileField("File", upload_to=GeneratoreNomeFile('documenti/'),
                            validators=[valida_dimensione_file_8mb])
    sede = models.ForeignKey('anagrafica.Sede', db_index=True, on_delete=models.PROTECT)
    expires = models.DateField(null=True)

    class Meta:
        verbose_name = 'Documenti Comitato'
        verbose_name_plural = "Documenti Comitato"
        app_label = 'gestione_file'


class Immagine(InterfacciaJorvik, BaseImage):
    url_documento = models.URLField(_('URL Documento'), default='', blank=True)
    downloads = models.PositiveIntegerField("Downloads", db_index=True, default=0)
    data_pubblicazione = models.DateTimeField(_('Data pubblicazione'), default=now)

    class Meta:
        abstract = False
        app_label = 'gestione_file'
        verbose_name = 'immagine'
        verbose_name_plural = 'immagini'

    def icona(self):
        if self.url_documento:
            return 'fa fa-external-link-square'
        else:
            return 'fa fa-file-image-o'

    @property
    def image(self):
        return self.immagine


class DocumentoSegmento(BaseSegmento):
    _oggetto_collegato = File
