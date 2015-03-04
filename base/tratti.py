"""
Questo modulo e' una collezione di Tratti.

I tratti possono essere aggiunti ai modelli per aggiugere
dei set di funzionalita'. Si noti bene che ogni tratto
potrebbe necessitare l'implementazione di metodi o proprieta'
particolari. Fare riferimento alla documentazione del tratto
utilizzato.
"""
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from anagrafica.costanti import ESTENSIONE, ESTENSIONE_MINORE


class ConMarcaTemporale(models.Model):
    """
    Aggiunge le marche temporali automatiche di creazione ed ultima modifica.
    """

    class Meta:
        abstract = True

    creazione = models.DateTimeField(auto_now_add=True, db_index=True)
    ultima_modifica = models.DateTimeField(auto_now=True, db_index=True)


class ConEstensione(models.Model):
    """
    Aggiunge un Comitato ed un livello di estensione dell'oggetto.
    """

    comitato = models.ForeignKey("anagrafica.Comitato", db_index=True)
    estensione = models.CharField("Estensione", max_length=1, choices=ESTENSIONE, db_index=True)

    def possibili_estensioni(self, comitato=None):
        """
        Dato un comitato, od il comitato gia' salvato, ritorna le possibili estensioni.
        :param comitato: Opzionale. Il comitato. Quello gia' salvato se non specificato.
        :return: (chiave, valore), (chiave, valore)
        """

        if comitato is None:
            comitato = self.comitato

        return (
            (chiave, valore) for (chiave, valore) in ESTENSIONE
            if chiave in ESTENSIONE_MINORE[comitato.estensione]
            or chiave == comitato.estensione
        )


class ConStorico(models.Model):
    """
    Aggiunge un inizio, una fine ed una verifica per attualita'.
    """

    class Meta:
        abstract = True

    # Puo' essere sovrascritto per aggiungere una ulteriore
    # condizione di attualita' (es. partecipazione confermata, ecc.)
    CONDIZIONE_ATTUALE_AGGIUNTIVA = Q()

    inizio = models.DateField("Inizio", db_index=True, null=False)
    fine = models.DateField("Fine", db_index=True, null=True, blank=True, default=None)

    @classmethod
    def query_attuale(cls, al_giorno=date.today()):
        """
        Restituisce l'oggetto Q per filtrare le entita' attuali.
        :param al_giorno: Giorno per considerare la verifica per l'attuale. Default oggi.
        :return: Q!
        """

        return Q(
            Q(inizio__lte=al_giorno),
            Q(fine__isnull=True) | Q(fine__gte=al_giorno),
            cls.CONDIZIONE_ATTUALE_AGGIUNTIVA
        )

    def attuale(self, al_giorno=date.today()):
        """
        Controlla se l'entita' e' attuale o meno.
        :param al_giorno: Giorno per considerare la verifica per l'attuale. Default oggi.
        :return: True o False.
        """
        try:
            self.__class__.objects.get(self.query_attuale(al_giorno), pk=self.pk)

        except ObjectDoesNotExist:
            return False

        return True