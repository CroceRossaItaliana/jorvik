from django.db import models

from anagrafica.models import Sede
from curriculum.models import Titolo
from .segmenti import SEGMENTI, NOMI_SEGMENTI


class BaseSegmento(models.Model):

    nome = models.CharField(max_length=256)
    segmento = models.CharField(max_length=256, choices=NOMI_SEGMENTI)
    _metodo = None

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome

    def filtro(self):
        if not self._metodo:
            self._metodo = SEGMENTI.get(self.get_segmento_display())
        return self._metodo

#class DocumentoSegmento(BaseSegmento):
    # FK a documento
#    pass

#class NotiziaSegmento(BaseSegmento):
    # FK a notizia
#    pass
