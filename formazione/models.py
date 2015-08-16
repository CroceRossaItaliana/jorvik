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

    # Tipologia di corso
    BASE = 'BA'
    TIPO = (
        (BASE, 'Corso Base'),
    )
    tipo = models.CharField('Tipo', choices=TIPO, max_length=2, default=BASE)

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

    class Meta:
        verbose_name = "Corso di formazione"
        verbose_name_plural = "Corsi di formazione"


class Partecipazione(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):

    persona = models.ForeignKey(Persona, related_name='partecipazioni_corsi')
    corso = models.ForeignKey(Corso, related_name='partecipazioni')

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class Lezione(ModelloSemplice, ConMarcaTemporale, ConGiudizio):

    corso = models.ForeignKey(Corso, related_name='lezioni')

    class Meta:
        verbose_name_plural = "Lezioni"


class Assenza(ModelloSemplice, ConMarcaTemporale):

    corso = models.ForeignKey(Corso, related_name='assenze')

    class Meta:
        verbose_name_plural = "Assenze"


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

    def corsi(self, tipo=Corso.BASE, stato=Corso.ATTIVO, **kwargs):
        """
        Ritorna un elenco di Corsi (Base) nelle vicinanze dell'Aspirante.
        :param tipo: Il tipo di corso. Default=Corso.BASE.
        :param stato: Stato del corso. Default=Corso.ATTIVO.
        :return: Un elenco di Corsi.
        """
        return self.nel_raggio(Corso.objects.filter(tipo=tipo, stato=stato, **kwargs))

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

