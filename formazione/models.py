# coding=utf-8

"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
import datetime

from anagrafica.models import Sede, Persona
from base.models import ConAutorizzazioni
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConDelegati
from social.models import ConCommenti, ConGiudizio
from django.db import models


class Corso(ModelloSemplice, ConDelegati, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio):

    class Meta:
        abstract = True

    # Stato del corso
    PREPARAZIONE = 'P'
    ATTIVO = 'A'
    INIZIATO = 'I'
    ANNULLATO = 'A'
    TERMINATO = 'T'  # TODO Terminare il corso automaticamente!
    STATO = (
        (PREPARAZIONE, 'In preparazione'),
        (ATTIVO, 'Attivo'),
        (INIZIATO, 'Iniziato'),
        (TERMINATO, 'Terminato'),
        (ANNULLATO, 'Annullato'),
    )
    stato = models.CharField('Stato', choices=STATO, max_length=1, default=PREPARAZIONE)
    sede = models.ForeignKey(Sede, related_query_name='%(class)s_corso', help_text="La Sede organizzatrice del Corso.")


class CorsoBase(Corso):

    ## Tipologia di corso
    #BASE = 'BA'
    #TIPO = (
    #    (BASE, 'Corso Base'),
    #)
    #tipo = models.CharField('Tipo', choices=TIPO, max_length=2, default=BASE)

    class Meta:
        verbose_name = "Corso Base"
        verbose_name_plural = "Corsi Base"

    data_inizio = models.DateTimeField(blank=False, null=False, help_text="La data di inizio del corso. "
                                                                          "Utilizzata per la gestione delle iscrizioni.")
    data_esame = models.DateTimeField(blank=False, null=False)
    progressivo = models.SmallIntegerField(blank=False, null=False, db_index=True)
    anno = models.SmallIntegerField(blank=False, null=False, db_index=True)

    def __str__(self):
        return self.nome

    @property
    def url(self):
        return "/aspirante/corso-base/%d/" % (self.pk,)

    @property
    def nome(self):
        return "Corso Base %d/%d (%s)" % (self.progressivo, self.anno, self.sede)

    @property
    def link(self):
        return "<a href=\"%s\" target=\"_new\">%s</a>" % (self.url, self.nome)

    @property
    def url_direttori(self):
        return "/formazione/corsi-base/%d/direttori/" % (self.pk,)

    @classmethod
    def nuovo(cls, anno=datetime.date.today().year, **kwargs):
        """
        Metodo per creare un nuovo corso. Crea progressivo automaticamente.
        :param anno: Anno di creazione del corso.
        :param kwargs: Parametri per la creazione del corso.
        :return:
        """

        try:  # Per il progressivo, cerca ultimo corso
            ultimo = CorsoBase.objects.filter(anno=anno).latest('progressivo')
            progressivo = ultimo.progressivo + 1

        except:  # Se non esiste, inizia da 1
            progressivo = 1

        c = CorsoBase(
            anno=anno,
            progressivo=progressivo,
            **kwargs
        )
        c.save()
        return c


class PartecipazioneCorsoBase(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):

    persona = models.ForeignKey(Persona, related_name='partecipazioni_corsi')
    corso = models.ForeignKey(CorsoBase, related_name='partecipazioni')

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class LezioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    corso = models.ForeignKey(CorsoBase, related_name='lezioni')

    class Meta:
        verbose_name_plural = "Lezioni Corsi Base"


class AssenzaCorsoBase(ModelloSemplice, ConMarcaTemporale):

    corso = models.ForeignKey(CorsoBase, related_name='assenze')

    class Meta:
        verbose_name_plural = "Assenze ai Corsi Base"


class Aspirante(ModelloSemplice, ConGeolocalizzazioneRaggio, ConMarcaTemporale):

    persona = models.OneToOneField(Persona, related_name='aspirante')

    # Numero minimo di Comitati nelle vicinanze
    MINIMO_COMITATI = 15
    RAGGIO_STEP = 1

    # Massimo iterazioni nella ricerca
    MASSIMO_ITERAZIONI = 50

    class Meta:
        verbose_name_plural = "Aspiranti"

    def __str__(self):
        return "Aspirante %s" % (self.persona.nome_completo,)

    def sedi(self, tipo=Sede.COMITATO, **kwargs):
        """
        Ritorna un elenco di Comitati (Sedi) nelle vicinanze dell'Aspirante.
        :param tipo: Il tipo di sede. Default=Sede.COMITATO.
        :return: Un elenco di Sedi.
        """
        return self.nel_raggio(Sede.objects.filter(tipo=tipo, **kwargs))

    def corsi(self, stato=Corso.ATTIVO, **kwargs):
        """
        Ritorna un elenco di Corsi (Base) nelle vicinanze dell'Aspirante.
        :param stato: Stato del corso. Default=Corso.ATTIVO.
        :return: Un elenco di Corsi.
        """
        return self.nel_raggio(CorsoBase.objects.filter(stato=stato, **kwargs))

    def calcola_raggio(self):
        """
        Calcola il raggio minimo necessario.
        :return: Il nuovo raggio.
        """
        iterazione = 0
        self.raggio = .0
        while True:
            iterazione += 1
            self.raggio += self.RAGGIO_STEP
            self.save()

            if iterazione >= self.MASSIMO_ITERAZIONI or self.sedi().count() >= self.MINIMO_COMITATI:
                break

        return self.raggio

    def post_locazione(self):
        """
        Ricalcola il raggio automaticamente ogni volta che viene impostata
        una nuova locazione.
        """
        self.calcola_raggio()
        return super(Aspirante, self).post_locazione()
