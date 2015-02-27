from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale

__author__ = 'alfioemanuele'


class Giudizio(ConMarcaTemporale, ModelloSemplice):
    """
    Rappresenta un giudizio sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConGiudizio ed i suoi metodi.
    """

    class Meta:
        verbose_name_plural = "Giudizi"

    autore = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="giudizi")
    positivo = models.BooleanField("Positivo", db_index=True, default=True)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')


class Commento(ConMarcaTemporale, ModelloSemplice):
    """
    Rappresenta un commento sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConCommento ed i suoi metodi.
    """

    class Meta:
        verbose_name_plural = "Commenti"

    autore = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="commenti")
    commento = models.TextField("Testo del commento")
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')


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