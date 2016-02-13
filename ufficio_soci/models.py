import random
from datetime import timezone, date

from django.db import models
from django.db.models import Q, Max

from anagrafica.models import Persona, Appartenenza, Sede
from base.files import PDF
from base.models import ModelloSemplice, ConAutorizzazioni, ConVecchioID
from base.tratti import ConMarcaTemporale, ConPDF
from base.utils import concept, UpperCaseCharField, ean13_carattere_di_controllo, questo_anno, oggi
from posta.models import Messaggio

__author__ = 'alfioemanuele'


class Tesserino(ModelloSemplice, ConMarcaTemporale, ConPDF):

    class Meta:
        verbose_name = "Richiesta Tesserino Associativo"
        verbose_name_plural = "Richieste Tesserino Associativo"

    persona = models.ForeignKey('anagrafica.Persona', related_name='tesserini', on_delete=models.CASCADE)
    emesso_da = models.ForeignKey('anagrafica.Sede', related_name='tesserini_emessi', on_delete=models.PROTECT)

    RILASCIO = "RIL"
    RINNOVO = "RIN"
    DUPLICATO = "DUP"
    TIPO_RICHIESTA = (
        (RILASCIO, "Rilascio"),
        (RINNOVO, "Rinnovo"),
        (DUPLICATO, "Duplicato"),
    )
    tipo_richiesta = models.CharField(max_length=3, choices=TIPO_RICHIESTA, default=RILASCIO, db_index=True)

    RIFIUTATO = "RIF"
    RICHIESTO = "ATT"
    ACCETTATO = "OK"
    STATO_RICHIESTA = (
        (RIFIUTATO, "Emissione Rifiutata"),
        (RICHIESTO, "Emissione Richiesta"),
        (ACCETTATO, "Emissione Accettata"),
    )
    stato_richiesta = models.CharField(max_length=3, choices=STATO_RICHIESTA, default=RICHIESTO, db_index=True)
    motivo_richiesta = models.CharField(max_length=512, blank=True, null=True)
    motivo_rifiutato = models.CharField(max_length=512, blank=True, null=True)

    STAMPATO = "STAMPAT"
    SPEDITO_CASA = "SP_CASA"
    SPEDITO_SEDE = "SP_SEDE"
    STATO_EMISSIONE = (
        (STAMPATO, "Stampato"),
        (SPEDITO_CASA, "Spedito a casa"),
        (SPEDITO_SEDE, "Spedito alla Sede CRI")
    )
    stato_emissione = models.CharField(max_length=8, choices=STATO_EMISSIONE, blank=True, null=True, default=None)

    valido = models.BooleanField(default=False, db_index=True)

    codice = UpperCaseCharField(max_length=13, unique=True, db_index=True, null=True, default=None)

    richiesto_da = models.ForeignKey('anagrafica.Persona', related_name='tesserini_stampati_richiesti', null=False, on_delete=models.CASCADE)

    confermato_da = models.ForeignKey('anagrafica.Persona', related_name='tesserini_confermati', null=True, on_delete=models.SET_NULL)
    data_conferma = models.DateTimeField(null=True, db_index=True)

    riconsegnato_a = models.ForeignKey('anagrafica.Persona', related_name='tesserini_riconsegnati', null=True, on_delete=models.SET_NULL)
    data_riconsegna = models.DateTimeField(null=True, db_index=True)

    def assicura_presenza_codice(self):
        """
        Questa funzione si assicura che il tesserino attuale abbia un codice.
         Se il codice e' gia' stato assegnato a questa richiesta, non viene
         mai sovrascritto.
        """
        if not self.codice:
            self._assegna_nuovo_codice()
        return self.codice

    @classmethod
    def _genera_nuovo_codice(cls):
        """
        Ottiene un codice vergine.
        """
        while True:
            # Genera un codice casuale
            interno = str(random.randint(10000000, 99999999))
            codice = "8016%s" % (interno,)
            codice = "%s%s" % (
                codice, ean13_carattere_di_controllo(codice),
            )
            if not cls.objects.filter(codice=codice).exists():
                return codice

    def _assegna_nuovo_codice(self):
        """
        NON USARE DIRETTAMENTE! Genera un nuovo codice.
         Se vuoi assicurarti che il tesserino abbia un codice,
         usa invece il metodo assicura_presenza_codice.
        """
        self.codice = Tesserino._genera_nuovo_codice()

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
            "Tesserino %s.pdf" % self.codice,
            modello='pdf_tesserino.html',
            corpo={
                "tesserino": self,
                "persona": self.persona,
                "sede": self.persona.sede_riferimento(al_giorno=self.creazione),
            },
            formato=PDF.FORMATO_CR80,
            orientamento=PDF.ORIENTAMENTO_ORIZZONTALE,
        )
        return pdf


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

    anno = models.SmallIntegerField(db_index=True, unique=True, default=questo_anno)
    inizio = models.DateField(db_index=True, default=oggi)

    quota_attivo = models.FloatField(default=8.00)
    quota_ordinario = models.FloatField(default=16.00)
    quota_benemerito = models.FloatField(default=20.00)
    quota_aspirante = models.FloatField(default=20.00)
    quota_sostenitore = models.FloatField(default=20.00)

    @property
    def accetta_pagamenti(self):
        return self.stato == self.APERTO and oggi() >= self.inizio

    @classmethod
    def aperto_anno(cls, anno):
        try:
            t = Tesseramento.objects.get(anno=anno)
            return t.accetta_pagamenti
        except Tesseramento.DoesNotExist:
            return False

    def importo_da_pagare(self, socio):

        if socio.volontario:  # Quota socio attivo
            return self.quota_attivo

        elif socio.ordinario:  # Quota socio ordinario
            return self.quota_ordinario

        elif hasattr(socio, 'aspirante'):  # Quota Aspirante
            return self.quota_aspirante

        return 0.0

    def passibili_pagamento(self, membri=Appartenenza.MEMBRO_SOCIO):
        """
        Ritorna un elenco di tutti i passibili di pagamento di quota
         associativa per il tesseramento in essere.
        :param membri: Lista o tupla di appartenenze da considerare
        :return: QuerySet<Persona>
        """

        # Soci che hanno almeno una appartenenza confermata
        #  durante l'anno presso un Comitato CRI
        return Persona.objects.filter(
            Appartenenza.query_attuale_in_anno(self.anno).via("appartenenze"),              # Membri nell'anno
            appartenenze__membro__in=membri,                                                # ...di un socio cri
            appartenenze__sede__tipo=Sede.COMITATO,                                         # ...presso un Comitato
        )

    def _q_pagante(self):
        return Q(
            quote__tipo=Quota.QUOTA_SOCIO,      # Solo quote socio
            quote__stato=Quota.REGISTRATA,      # Escludi quote annullate
        )

    def _q_ordinari(self, solo_paganti=True):
        return Q(  # Ordinario che ha pagato almeno quota ordinario
                    Appartenenza.query_attuale_in_anno(self.anno).via("appartenenze"),
                    self._q_pagante() if solo_paganti else Q(),
                    appartenenze__membro=Appartenenza.ORDINARIO,
                )

    def _q_volontari(self, solo_paganti=True):
        return Q(  # Oppure volontario che ha pagato almeno quota volontario
                    Appartenenza.query_attuale_in_anno(self.anno).via("appartenenze"),
                    self._q_pagante() if solo_paganti else Q(),
                    appartenenze__membro=Appartenenza.VOLONTARIO,
                )

    def paganti(self, attivi=True, ordinari=True):
        """
        Ritorna un elenco di persone che hanno pagato la quota associativa
         per il tesseramento in essere.
        :return: QuerySet<Persona>
        """
        if (not attivi) and (not ordinari):
            return Persona.objects.none()

        a = Q()

        if attivi and ordinari:
            q = self._q_ordinari(solo_paganti=True) | self._q_volontari(solo_paganti=True)

        elif attivi:
            a = self._q_volontari(solo_paganti=True)

        else:
            a = self._q_ordinari(solo_paganti=True)

        return Persona.objects.filter(pk__in=Persona.objects.filter(
            a,
            quote__anno=self.anno,
            quote__stato=Quota.REGISTRATA,
        ))

    def non_paganti(self, attivi=True, ordinari=True):
        """
        Ritorna un elenco di persone che sono passibili per la quota associativa
         per il tesseramento in essere MA non sono paganti (non hanno gia' pagato).
        :return: QuerySet<Persona>
        """
        l = []
        if attivi:
            l += [Appartenenza.VOLONTARIO]
        if ordinari:
            l += [Appartenenza.ORDINARIO]
        return self.passibili_pagamento(membri=l).exclude(pk__in=self.paganti(attivi=attivi, ordinari=ordinari))

    def non_pagante(self, persona, **kwargs):
        return self.non_paganti(**kwargs).filter(pk=persona.pk).exists()

    def pagante(self, persona, **kwargs):
        return self.paganti(**kwargs).filter(pk=persona.pk).exists()

    @classmethod
    def anni_scelta(cls):
        return ((y, y) for y in [x['anno'] for x in cls.objects.all().values("anno")])

    @classmethod
    def ultimo_anno(cls):
        try:
            return cls.objects.latest('anno').anno
        except Tesseramento.DoesNotExist:
            return None




class Quota(ModelloSemplice, ConMarcaTemporale, ConPDF, ConVecchioID):

    persona = models.ForeignKey('anagrafica.Persona', related_name='quote', db_index=True, on_delete=models.CASCADE)
    appartenenza = models.ForeignKey('anagrafica.Appartenenza', null=True, related_name='quote', db_index=True, on_delete=models.SET_NULL)
    sede = models.ForeignKey('anagrafica.Sede', related_name='quote', db_index=True, on_delete=models.PROTECT)

    progressivo = models.IntegerField(db_index=True)
    anno = models.SmallIntegerField(db_index=True, default=questo_anno)

    data_versamento = models.DateField(help_text="La data di versamento dell'importo.")
    data_annullamento = models.DateField(null=True, blank=True)
    registrato_da = models.ForeignKey('anagrafica.Persona', related_name='quote_registrate', null=True, on_delete=models.SET_NULL)
    annullato_da = models.ForeignKey('anagrafica.Persona', related_name='quote_annullate', blank=True, null=True, on_delete=models.SET_NULL)

    REGISTRATA = 'R'
    ANNULLATA = 'X'
    STATO = (
        (REGISTRATA, "Registrata"),
        (ANNULLATA, "Annullata"),
    )
    stato = models.CharField(max_length=1, db_index=True, choices=STATO, default=REGISTRATA)

    QUOTA_SOCIO = 'Q'
    QUOTA_SOSTENITORE = 'S'
    RICEVUTA = 'R'
    TIPO = (
        (QUOTA_SOCIO, "Quota Socio"),
        (QUOTA_SOSTENITORE, "Quota Sostenitore"),
        (RICEVUTA, "Ricevuta")
    )
    tipo = models.CharField(max_length=1, default=QUOTA_SOCIO, choices=TIPO)

    importo = models.FloatField()
    importo_extra = models.FloatField(default=0.0)

    causale = models.CharField(max_length=512)
    causale_extra = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name_plural = "Quote"
        unique_together = ('progressivo', 'anno', 'sede',)
        ordering = ['anno', 'progressivo']

    def tesseramento(self):
        """
        Ottiene l'oggetto tesseramento correlato.
        """
        return Tesseramento.objects.get(anno=self.anno)

    @classmethod
    def nuova(cls, appartenenza, data_versamento, registrato_da, importo,
              causale, tipo=QUOTA_SOCIO, invia_notifica=True, **kwargs):
        q = Quota(
            appartenenza=appartenenza,
            sede=appartenenza.sede.comitato,
            persona=appartenenza.persona,
            data_versamento=data_versamento,
            registrato_da=registrato_da,
            importo=importo,
            causale=causale,
            tipo=tipo,
            **kwargs
        )

        # Scompone l'importo in Quota e Extra (Donazione)
        da_pagare = q.tesseramento().importo_da_pagare(q.persona)
        if importo > da_pagare:
            q.importo = da_pagare
            q.importo_extra = importo - da_pagare
            q.causale_extra = "Donazione"

        q.anno = data_versamento.year
        q.progressivo = q._genera_progessivo()
        q.save()

        if invia_notifica:
            q._invia_notifica_registrazione()

        return q

    @classmethod
    @concept
    def per_sede(cls, sede):
        return Q(
            sede=sede.comitato,
        )

    def _genera_progessivo(self):
        anno = self.anno
        sede = self.sede

        prec = Quota.per_sede(sede).filter(anno=anno) \
                    .aggregate(max=Max('progressivo'))['max'] or 0
        return prec + 1

    @property
    def importo_totale(self):
        return self.importo + self.importo_extra

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
          nome="Ricevuta %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "quota": self,
          },
          modello="pdf_ricevuta.html",
        )
        return pdf

    def annulla(self, annullato_da, invia_notifica=True):
        self.stato = self.ANNULLATA
        self.annullato_da = annullato_da
        self.data_annullamento = oggi()
        self.save()
        if invia_notifica:
            self._invia_notifica_annullamento()

    def _invia_notifica_registrazione(self):
        Messaggio.costruisci_e_invia(
            oggetto="Ricevuta %d del %d: %s" % (
                self.progressivo, self.anno, self.causale
            ),
            modello="email_ricevuta_nuova_notifica.html",
            corpo={"ricevuta": self},
            mittente=self.registrato_da,
            destinatari=[self.persona],
        )

    def _invia_notifica_annullamento(self):
        Messaggio.costruisci_e_invia(
            oggetto="ANNULLATA Ricevuta %d del %d" % (
                self.progressivo, self.anno
            ),
            modello="email_ricevuta_annullata_notifica.html",
            corpo={"ricevuta": self},
            mittente=self.registrato_da,
            destinatari=[self.persona],
        )
