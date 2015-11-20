# coding=utf-8

"""
Questo modulo definisce i modelli del modulo Attivita' di Gaia.
"""
from django.db import models

from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati
from base.tratti import ConMarcaTemporale, ConDelegati
from base.geo import ConGeolocalizzazione


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale, ConGiudizio, ConCommenti,
               ConAllegati, ConDelegati):

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
    sede = models.ForeignKey('anagrafica.Sede', related_name='attivita')
    area = models.ForeignKey("Area", related_name='attivita')
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None, related_name='attivita_estensione')
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


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    class Meta:
        verbose_name_plural = "Turni"

    attivita = models.ForeignKey(Attivita, related_name='turni')

    nome = models.CharField(max_length=128, default="Nuovo turno", db_index=True)

    prenotazione = models.DateTimeField("Prenotazione entro", db_index=True, null=False)
    inizio = models.DateTimeField("Inizio", db_index=True, null=False)
    fine = models.DateTimeField("Fine", db_index=True, null=True, blank=True, default=None)

    minimo = models.SmallIntegerField(db_index=True, default=1)
    massimo = models.SmallIntegerField(db_index=True, null=True, default=None)

    def __str__(self):
        return "%s (%s)" % (self.nome, self.attivita.nome if self.attivita else "Nessuna attività")

    def partecipazioni_confermate(self):
        return Partecipazione.con_esito_ok().filter(turno=self)

    @property
    def scoperto(self):
        return self.partecipazioni_confermate().count() < self.minimo

    @property
    def url(self):
        return "%sturni/%d/" % (self.attivita.url, self.pk)

    @property
    def link(self):
        return "<a href='%s' target='_new'>%s</a>" % (
            self.url, self.nome
        )


class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"

    RICHIESTA = 'K'
    RITIRATA = 'X'
    NON_PRESENTATO = 'N'
    STATO = (
        (RICHIESTA, "Part. Richiesta"),
        (RITIRATA, "Part. Ritirata"),
        (NON_PRESENTATO, "Non presentato/a"),
    )

    persona = models.ForeignKey("anagrafica.Persona", related_name='partecipazioni')
    turno = models.ForeignKey(Turno, related_name='partecipazioni')
    stato = models.CharField(choices=STATO, default=RICHIESTA, max_length=1, db_index=True)

    def __str__(self):
        return "%s a %s" % (self.persona.codice_fiscale, str(self.turno))

    @classmethod
    def ritirate(cls):
        """
        Ottiene il QuerySet per tutte le partecipazioni ritirate.
        """
        return cls.con_esito_ritirata()

    @classmethod
    def confermate(cls):
        """
        Ottiene il QuerySet per tutte le partecipazioni confermate.
        """
        return cls.con_esito_ok()

    @classmethod
    def negate(cls):
        """
        Ottiene il QuerySet per tutte le partecipazioni negate.
        """
        return cls.con_esito_no()

    @property
    @classmethod
    def in_attesa(cls):
        """
        Ottiene il QuerySet per tutte le partecipazioni in attesa di autorizzazione.
        """
        return cls.con_esito_pending

    def ritira(self):
        """
        Ritira la partecipazione, annulla eventuali richieste pendenti.
        """
        self.stato = self.RITIRATA
        self.autorizzazioni_ritira()

    def autorizzazione_concessa(self):
        """
        (Automatico)
        Invia notifica di autorizzazione concessa.
        """
        # TODO
        pass

    def autorizzazione_negata(self, motivo=None):
        """
        (Automatico)
        Invia notifica di autorizzazione negata.
        :param motivo: Motivazione, se presente.
        """
        # TODO
        pass



class Area(ModelloSemplice, ConMarcaTemporale, ConDelegati):

    sede = models.ForeignKey('anagrafica.Sede', related_name='aree')
    nome = models.CharField(max_length=256, db_index=True, default='Generale', blank=False)
    obiettivo = models.SmallIntegerField(null=False, blank=False, default=1, db_index=True)

    class Meta:
        verbose_name_plural = "Aree"

    def __str__(self):
        return "%s (Ob. %d)" % (self.nome, self.obiettivo)