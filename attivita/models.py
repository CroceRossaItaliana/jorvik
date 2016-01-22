# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""
from datetime import timedelta
from math import floor

from django.db import models
from django.db.models import Q
from django.utils import timezone

from anagrafica.permessi.costanti import MODIFICA
from base.utils import concept
from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati, ConVecchioID
from base.tratti import ConMarcaTemporale, ConDelegati
from base.geo import ConGeolocalizzazione

class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti,
               ConAllegati, ConDelegati, ConVecchioID):

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"

    BOZZA = 'B'
    VISIBILE = 'V'
    STATO = (
        (BOZZA, "Bozza"),
        (VISIBILE, "Visibile")
    )

    CHIUSA = 'C'
    APERTA = 'A'
    APERTURA = (
        (CHIUSA, 'Chiusa'),
        (APERTA, 'Aperta')
    )

    nome = models.CharField(max_length=255, default="Nuova attività", db_index=True)
    sede = models.ForeignKey('anagrafica.Sede', related_name='attivita', on_delete=models.PROTECT)
    area = models.ForeignKey("Area", related_name='attivita', on_delete=models.SET_NULL, null=True)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None, related_name='attivita_estensione', on_delete=models.PROTECT)
    stato = models.CharField(choices=STATO, default=BOZZA, max_length=1, db_index=True)
    apertura = models.CharField(choices=APERTURA, default=APERTA, max_length=1, db_index=True)
    descrizione = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    @property
    def url(self):
        return "/attivita/scheda/%d/" % (self.pk,)

    @property
    def link(self):
        return "<a href='%s' target='_new'>%s</a>" % (
            self.url, self.nome
        )

    @property
    def url_mappa(self):
        return self.url + "mappa/"

    @property
    def url_turni(self):
        return self.url + "turni/"

    def pagina_turni_oggi(self):
        posizione = Turno.objects.filter(
            attivita=self,
            fine__lte=timezone.now(),
        ).count() + 1
        return floor(posizione / Turno.PER_PAGINA) + 1

    @property
    def url_modifica(self):
        return self.url + "modifica/"

    @property
    def url_mappa_modifica(self):
        return self.url_modifica

    @property
    def url_turni_modifica(self):
        return self.url_turni + "modifica/"

    @property
    def url_report(self):
        return self.url + "report/"

    def commento_notifica_destinatari(self, mittente):
        from anagrafica.models import Persona

        # Come destinatari, sempre i delegati dell'attivita'... tranne me.
        destinatari = self.delegati_attuali().exclude(pk=mittente.pk)

        # Se posso modificare l'attività, notifica a tutti
        #  i partecipanti (sono presidente, oppure referente).
        if mittente.permessi_almeno(self, MODIFICA):
            destinatari |= Persona.objects.filter(
                partecipazioni__turno__attivita=self,
                partecipazioni__stato=Partecipazione.RICHIESTA,
                partecipazioni__turno__inizio__gte=timezone.now() - timedelta(days=120),
            )

        return destinatari.distinct()

    def turni_futuri(self, *args, **kwargs):
        return Turno.query_futuri(
            *args,
            attivita=self,
            **kwargs
        )


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    class Meta:
        verbose_name_plural = "Turni"
        ordering = ['inizio', 'fine', 'id',]

    attivita = models.ForeignKey(Attivita, related_name='turni', on_delete=models.CASCADE)

    nome = models.CharField(max_length=128, default="Nuovo turno", db_index=True)

    prenotazione = models.DateTimeField("Prenotazione entro", db_index=True, null=False)
    inizio = models.DateTimeField("Inizio", db_index=True, null=False)
    fine = models.DateTimeField("Fine", db_index=True, null=True, blank=True, default=None)

    minimo = models.SmallIntegerField(db_index=True, default=1)
    massimo = models.SmallIntegerField(db_index=True, null=True, default=None)

    PER_PAGINA = 10

    def __str__(self):
        return "%s (%s)" % (self.nome, self.attivita.nome if self.attivita else "Nessuna attività")

    @property
    def scoperto(self):
        return self.partecipazioni_confermate().count() < self.minimo

    @property
    def futuro(self):
        return self.fine > timezone.now()

    @property
    def url(self):
        return "%sturni/link-permanente/%d/" % (self.attivita.url, self.pk)

    @property
    def link(self):
        return "<a href='%s' target='_new'>%s</a>" % (
            self.url, self.nome
        )

    @classmethod
    @concept
    def query_futuri(cls, *args, ora=timezone.now(), **kwargs):
        return Q(
            *args,
            fine__gt=ora,
            **kwargs
        )

    def elenco_posizione(self):
        """
        :return: Ottiene la posizione approssimativa di questo turno in elenco (5=quinto).
        """
        return Turno.objects.filter(
            attivita=self.attivita,
            inizio__lte=self.inizio,
            fine__lte=self.fine,
        ).exclude(pk=self.pk).count() + 1

    def elenco_pagina(self):
        return floor((self.elenco_posizione() / self.PER_PAGINA) + 1)

    def partecipazioni_in_attesa(self):
        return Partecipazione.con_esito_pending(turno=self)

    def partecipazioni_confermate(self):
        return Partecipazione.con_esito_ok(turno=self)

    def partecipazioni_negate(self):
        return Partecipazione.con_esito_no(turno=self)

    def partecipazioni_ritirate(self):
        return Partecipazione.con_esito_ritirata(turno=self)




class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"

    RICHIESTA = 'K'
    NON_PRESENTATO = 'N'
    STATO = (
        (RICHIESTA, "Part. Richiesta"),
        (NON_PRESENTATO, "Non presentato/a"),
    )

    persona = models.ForeignKey("anagrafica.Persona", related_name='partecipazioni', on_delete=models.CASCADE)
    turno = models.ForeignKey(Turno, related_name='partecipazioni', on_delete=models.CASCADE)
    stato = models.CharField(choices=STATO, default=RICHIESTA, max_length=1, db_index=True)

    def __str__(self):
        return "%s a %s" % (self.persona.codice_fiscale, str(self.turno))

    def ritira(self):
        """
        Ritira la partecipazione, annulla eventuali richieste pendenti.
        """
        self.stato = self.RITIRATA
        self.autorizzazioni_ritira()

    def autorizzazione_concessa(self, modulo):
        """
        (Automatico)
        Invia notifica di autorizzazione concessa.
        """
        # TODO
        pass

    def autorizzazione_negata(self, modulo=None):
        """
        (Automatico)
        Invia notifica di autorizzazione negata.
        :param motivo: Motivazione, se presente.
        """
        # TODO
        pass



class Area(ModelloSemplice, ConMarcaTemporale, ConDelegati):

    sede = models.ForeignKey('anagrafica.Sede', related_name='aree', on_delete=models.PROTECT)
    nome = models.CharField(max_length=256, db_index=True, default='Generale', blank=False)
    obiettivo = models.SmallIntegerField(null=False, blank=False, default=1, db_index=True)

    class Meta:
        verbose_name_plural = "Aree"

    def __str__(self):
        return "%s (Ob. %d)" % (self.nome, self.obiettivo)