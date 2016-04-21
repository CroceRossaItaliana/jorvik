from django.db import models

from segmenti.models import BaseSegmento


class NotiziaTest(models.Model):
    testo = models.CharField(max_length=256)


class NotiziaTestSegmento(BaseSegmento):
    notizia = models.ForeignKey(NotiziaTest, related_name="segmenti")
