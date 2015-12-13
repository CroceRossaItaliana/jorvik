# coding=utf-8

"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
from anagrafica.models import Sede, Persona
from base.models import ConAutorizzazioni
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale
from social.models import ConCommenti, ConGiudizio
from django.db import models


class Corso(ModelloSemplice, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio):

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
    sede = models.ForeignKey(Sede, related_query_name='%(class)s_corso')


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

    data_inizio = models.DateTimeField(blank=False, null=False)
    data_esame = models.DateTimeField(blank=False, null=False)




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
    MINIMO_COMITATI = 10
    RAGGIO_STEP = .1

    # Massimo iterazioni nella ricerca
    MASSIMO_ITERAZIONI = 25

    class Meta:
        verbose_name_plural = "Aspiranti"

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

