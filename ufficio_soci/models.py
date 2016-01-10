from datetime import timezone

from django.db import models

from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale
from base.utils import concept

__author__ = 'alfioemanuele'


class Dimissione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di Dimissione"
        verbose_name_plural = "Richieste di Dimissione"


class Tesserino(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta Tesserino Associativo"
        verbose_name_plural = "Richieste Tesserino Associativo"

    persona = models.ForeignKey('anagrafica.Persona', related_name='tesserini')


class Tesseramento(ModelloSemplice, ConMarcaTemporale):
    class Meta:
        verbose_name = "Tesseramento"
        verbose_name_plural = "Tesseramenti"

    APERTO = 'A'
    CHIUSO = 'C'
    STATO = (
        (APERTO, "Aperto"),
        (CHIUSO, "Chiuso"),
    )
    stato = models.CharField(choices=STATO, default=APERTO, max_length=1)

    def default_anno(self):
        return timezone.now().year

    def default_inizio(self):
        return timezone.now().date()

    anno = models.SmallIntegerField(db_index=True, unique=True, default=default_anno)
    inizio = models.DateField(db_index=True, default=default_inizio)

    quota_attivo = models.FloatField(default=8.00)
    quota_ordinario = models.FloatField(default=16.00)
    quota_benemerito = models.FloatField(default=20.00)
    quota_aspirante = models.FloatField(default=20.00)

    @property
    def accetta_pagamenti(self):
        return self.stato == self.APERTO and timezone.now().date() >= self.inizio

    def importo_da_pagare(self, socio):

        if socio.volontario:  # Quota socio attivo
            return self.quota_attivo

        elif socio.ordinario:  # Quota socio ordinario
            return self.quota_ordinario

        elif hasattr(socio, 'aspirante'):  # Quota Aspirante
            return self.quota_aspirante

        return 0.0


class Quota(ModelloSemplice, ConMarcaTemporale):


    def default_anno(self):
        """
        Anno di default per la compilazione di una nuova quota.
        """
        return timezone.now().year

    persona = models.ForeignKey('anagrafica.Persona', related_name='quote', db_index=True)
    appartenenza = models.ForeignKey('anagrafica.Appartenenza', null=True, related_name='quote', db_index=True)
    sede = models.ForeignKey('anagrafica.Sede', related_name='quote', db_index=True)

    progressivo = models.IntegerField(db_index=True)
    anno = models.SmallIntegerField(db_index=True, default=default_anno)

    data_versamento = models.DateField(help_text="La data di versamento dell'importo.")
    data_annullamento = models.DateField(null=True, blank=True)
    registrato_da = models.ForeignKey('anagrafica.Persona', related_name='quote_registrate')
    annullato_da = models.ForeignKey('anagrafica.Persona', related_name='quote_annullate', blank=True, null=True)

    REGISTRATA = 'R'
    ANNULLATA = 'X'
    STATO = (
        (REGISTRATA, "Registrata"),
        (ANNULLATA, "Annullata"),
    )
    stato = models.CharField(max_length=1, db_index=True, choices=STATO, default=REGISTRATA)

    importo = models.FloatField()
    importo_extra = models.FloatField(default=0.0)

    causale = models.CharField(max_length=512)
    causale_extra = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name_plural = "Quote"
        unique_together = ('progressivo', 'anno', 'sede',)

    def tesseramento(self):
        """
        Ottiene l'oggetto tesseramento correlato.
        """
        return Tesseramento.objects.get(anno=self.anno)

    @classmethod
    def nuova(cls, appartenenza, data_versamento, registrato_da, importo, causale, **kwargs):
        q = Quota(
            appartenenza=appartenenza,
            sede=appartenenza.sede.comitato,
            persona=appartenenza.persona,
            data_versamento=data_versamento,
            registrato_da=registrato_da,
            importo=importo,
            causale=causale,
            **kwargs
        )

        # Scompone l'importo in Quota e Extra (Donazione)
        da_pagare = q.tesseramento.importo_da_pagare(q.persona)
        if importo > da_pagare:
            q.importo = da_pagare
            q.importo_extra = importo - da_pagare
            q.causale_extra = "Donazione"

        q._assegna_progressivo()
        q.save()

    @classmethod
    @concept
    def per_sede(cls, sede):
        comitato = sede.comitato
        return cls.objects.filter(
            appartenenza__sede=comitato,
        )

    def _assegna_progressivo(self, sede, anno):
        try:  # Ottiene ultima quota
            ultima_quota = self.per_sede(sede).filter(anno=anno).latest('progressivo')
            return ultima_quota.progressivo + 1  # Ritorna prossimo progressivo

        except:  # Se prima quota
            return 1