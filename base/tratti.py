"""
Questo modulo e' una collezione di Tratti.

I tratti possono essere aggiunti ai modelli per aggiugere
dei set di funzionalita'. Si noti bene che ogni tratto
potrebbe necessitare l'implementazione di metodi o proprieta'
particolari. Fare riferimento alla documentazione del tratto
utilizzato.
"""
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.measure import D
from base.modelli import ModelloSemplice, Giudizio, Commento, Autorizzazione
from django.db import models


class ConMarcaTemporale(ModelloSemplice):
    """
    Aggiunge le marche temporali automatiche di creazione ed ultima modifica.
    """

    class Meta:
        abstract = True

    creazione = models.DateTimeField(auto_now_add=True, db_index=True)
    ultima_modifica = models.DateTimeField(auto_now=True, db_index=True)


class ConGiudizio(ModelloSemplice):
    """
    Aggiunge le funzionalita' di giudizio, stile social,
    positivi o negativi.
    """

    class Meta:
        abstract = True

    giudizi = GenericRelation(
        Giudizio,
        related_query_name='giudizi',
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    def giudizio_positivo(self, autore):
        """
        Registra un giudizio positivo
        :param autore: Autore del giudizio
        """
        self._giudizio(autore, True)


    def giudizio_negativo(self, autore):
        """
        Registra un giudizio negativo
        :param autore: Autore del giudizio
        """
        self._giudizio(autore, False)


    def _giudizio(self, autore, positivo):
        """
        Registra un giudizio
        :param autore: Autore del giudizio
        :param positivo: Vero se positivo, falso se negativo
        """
        g = self.giudizio_cerca(autore)
        if g:  # Se gia' esiste un giudizio, modifico il tipo
            g.positivo = positivo
        else:  # Altrimenti, ne registro uno nuovo
            g = Giudizio(
                oggetto=self,
                positivo=positivo,
                autore=autore
            )
        g.save()

    @property
    def giudizi_positivi(self):
        """
        Restituisce il numero di giudizi positivi associati all'oggetto.
        """
        return self._giudizi(self, True)

    @property
    def giudizi_negativi(self):
        """
        Restituisce il numero di giudizi negativi associati all'oggetto.
        """
        return self._giudizi(self, False)

    def _giudizi(self, positivo):
        """
        Restituisce il numero di giudizi positivi o negativi associati all'oggetto.
        """
        return self.giudizi.filter(positivo=positivo).count()

    def giudizio_cerca(self, autore):
        """
        Cerca il giudizio di un autore sull'oggetto. Se non presente,
        ritorna None.
        """
        g = self.giudizi.filter(autore=autore)[:1]
        if g:
            return g
        return None


class ConCommenti(ModelloSemplice):
    """
    Aggiunge la possibilita' di aggiungere commenti ad
    un oggetto.
    """

    class Meta:
        abstract = True

    commenti = GenericRelation(
        Commento,
        related_query_name='commenti',
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )


class ConAutorizzazioni(ModelloSemplice):
    """
    Aggiunge la possibilita' di aggiungere le funzionalita'
    di autorizzazione ad un ogetto.
    """

    class Meta:
        abstract = True

    autorizzazioni = GenericRelation(
        Autorizzazione,
        related_query_name='commenti',
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    def autorizzazione_concessa(self):
        """
        Sovrascrivimi! Ascoltatore per concessione autorizzazione.
        """
        pass

    def autorizzazione_negata(self):
        """
        Sovrascrivimi! Ascoltatore per negazione autorizzazione.
        """
        pass

    def autorizzazione_esito(self):
        """
        Restituisce l'esito delle richieste di autorizazzione.
        True per concessa, False per negata, None per pendente.
        """
        # Ci sono autorizzazioni negate?
        if self.autorizzazioni.filter(concessa=False).count():
            return False

        # Ci sono autorizzazioni pendenti?
        elif self.autorizazzioni.filter(concessa=None).count():
            return None

        # Sono tutte concesse.
        return True

    def autorizzazione_esito_in_testo(self):
        esito = self.autorizzazione_esito()
        if esito:
            return "Concessa"
        elif esito is None:
            return "In attesa"
        return "Negata"


class ConGeolocalizzazione(ModelloSemplice):
    """
    Aggiunge le funzioni di geolocalizzazione ad un oggetto.
    """

    class Meta:
        abstract = True

    geo = models.PointField()
    indirizzo = models.CharField("Indirizzo", max_length=255)

    def vicini(self, km):
        """
        Ritorna tutti gli oggetti simili vicini, nei pressi di x KM.
        :param km: Raggio di ricerca in kilometri.
        :return: Una ricerca filtrata.
        """
        self.objects.filter(geo__distance_lte=(self.geo, D(km=km)))


class ConGeolocalizzazioneRaggio(ModelloSemplice, ConGeolocalizzazione):
    """
    Aggiunge le funzioni di geolocalizzazione e quelle necessarie a rappresentare
    un'area circolare con raggio in kilometri.
    """

    raggio = models.FloatField("Raggio KM", default=0.0)

    class Meta:
        abstract = True

    def nel_raggio(self, ricerca):
        """
        Filtra una ricerca, per gli elementi nel raggio di questo elemento.
        :return: La ricerca filtrata
        """
        return ricerca.filter(geo__distance_lte=(self.geo, D(km=self.raggio)))

