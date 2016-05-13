# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models, transaction

from django.utils.translation import ugettext_lazy as _
from filer.models import File
from filer.models.abstract import BaseImage
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
        return reverse('scarica_file', args=(self.pk,))


class Documento(InterfacciaJorvik, File):
    url_documento = models.URLField(_('URL Documento'), default='', blank=True)
    downloads = models.PositiveIntegerField("Downloads", db_index=True, default=0)

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


class Immagine(InterfacciaJorvik, BaseImage):
    url_documento = models.URLField(_('URL Documento'), default='', blank=True)
    downloads = models.PositiveIntegerField("Downloads", db_index=True, default=0)

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


class DocumentoSegmento(BaseSegmento):
    _oggetto_collegato = File
