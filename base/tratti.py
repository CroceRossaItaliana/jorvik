"""
Questo modulo e' una collezione di Tratti.

I tratti possono essere aggiunti ai modelli per aggiugere
dei set di funzionalita'. Si noti bene che ogni tratto
potrebbe necessitare l'implementazione di metodi o proprieta'
particolari. Fare riferimento alla documentazione del tratto
utilizzato.
"""
from datetime import date, datetime
from django.apps import AppConfig, apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from anagrafica.costanti import ESTENSIONE, ESTENSIONE_MINORE
from base.utils import concept


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
    Aggiunge un Sede ed un livello di estensione dell'oggetto.
    """

    sede = models.ForeignKey("anagrafica.Sede", db_index=True)
    estensione = models.CharField("Estensione", max_length=1, choices=ESTENSIONE, db_index=True)

    def possibili_estensioni(self, sede=None):
        """
        Dato un sede, od il sede gia' salvato, ritorna le possibili estensioni.
        :param sede: Opzionale. Il sede. Quello gia' salvato se non specificato.
        :return: (chiave, valore), (chiave, valore)
        """

        if sede is None:
            sede = self.sede

        return (
            (chiave, valore) for (chiave, valore) in ESTENSIONE
            if chiave in ESTENSIONE_MINORE[sede.estensione]
            or chiave == sede.estensione
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
    @concept
    def query_attuale(cls, al_giorno=date.today(), **kwargs):
        """
        Restituisce l'oggetto Q per filtrare le entita' attuali.
        :param al_giorno: Giorno per considerare la verifica per l'attuale. Default oggi.
        :return: Q!
        """

        return Q(
            Q(inizio__lte=al_giorno),
            Q(fine__isnull=True) | Q(fine__gte=al_giorno),
            cls.CONDIZIONE_ATTUALE_AGGIUNTIVA,
            **kwargs
        )

    def attuale(self, al_giorno=date.today()):
        """
        Controlla se l'entita' e' attuale o meno.
        :param al_giorno: Giorno per considerare la verifica per l'attuale. Default oggi.
        :return: True o False.
        """
        return self.__class__.objects.filter(self.query_attuale(al_giorno).q, pk=self.pk).exists()


class ConDelegati(models.Model):
    """
    Aggiunge la possibilita' di gestire e aggiungere delegati.
    """

    class Meta:
        abstract = True

    deleghe = GenericRelation(
        'anagrafica.Delega',
        related_query_name="%(class)s",
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    @property
    def deleghe_attuali(self, al_giorno=datetime.today()):
        """
        Ottiene QuerySet per gli oggetti Delega validi ad un determinato giorno.
        :param al_giorno: Giorno da verificare. Se assente, oggi.
        :return: QuerySet di oggetti Delega.
        """
        Delega = apps.get_model(app_label='anagrafica', model_name='Delega')
        return self.deleghe.filter(Delega.query_attuale(al_giorno).q)

    @property
    def delegati_attuali(self, al_giorno=datetime.today()):
        """
        Ottiene QuerySet per gli oggetti Persona delegati ad un determinato giorno.
        :param al_giorno: Giorno da verificare. Se assente, oggi.
        :return: QuerySet di oggetti Persona.
        """
        Persona = apps.get_model(app_label='anagrafica', model_name='Persona')
        return Persona.objects.filter(delega__in=self.deleghe_attuali(al_giorno))

    def aggiungi_delegato(self, tipo, persona, firmatario=None, inizio=date.today(), fine=None):
        """
        Aggiunge un delegato per l'oggetto. Nel caso in cui una nuova delega (attuale)
         viene inserita, contemporaneamente ad una delega attuale per la stessa persona,
         sempre attuale, questa ultima viene estesa. Assicura quindi l'assenza di duplicati.
        :param tipo: Tipologia di delega.
        :param persona: La Persona da delegare al trattamento dell'oggetto.
        :param firmatario: Persona che inserisce la delega, opzionale.
        :param inizio: Inizio della delega. Se non specificato, inizio immediato.
        :param fine: Fine della delega. Se non specificato o None, fine indeterminata.
        :return: Oggetto delegato inserito.
        """

        # Se il nuovo inserimento e' attuale
        if inizio <= date.today() and (fine is None or fine >= date.today()):

            # Cerca eventuali deleghe pari gia' esistenti.
            delega_pari = self.deleghe_attuali.filter(persona=persona, tipo=tipo)

            # Se esiste, estende se necessario, e ritorna la delega passata
            if delega_pari.exists():
                delega_pari = delega_pari[0]
                delega_pari.inizio = min(delega_pari.inizio, inizio)
                delega_pari.fine = None if fine is None or delega_pari.fine is None else max(delega_pari.fine, fine)
                delega_pari.save()
                return delega_pari

        # Aggiungi la nuova delega.
        Delega = apps.get_model(app_label='anagrafica', model_name='Delega')
        d = Delega(oggetto=self, persona=persona, inizio=inizio, fine=fine, tipo=tipo, firmatario=firmatario)
        d.save()
        return d
