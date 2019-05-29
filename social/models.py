from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale


class Giudizio(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un giudizio sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConGiudizio ed i suoi metodi.
    """

    class Meta:
        verbose_name_plural = "Giudizi"
        permissions = (
            ("view_giudizio", "Can view giudizio"),
        )

    autore = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="giudizi", on_delete=models.CASCADE)
    positivo = models.BooleanField("Positivo", db_index=True, default=True)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True, on_delete=models.SET_NULL, null=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')


class Commento(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un commento sociale ad un oggetto generico.
    Utilizzare tramite il tratto ConCommento ed i suoi metodi.
    """

    class Meta:
        verbose_name_plural = "Commenti"
        app_label = "social"
        abstract = False
        permissions = (
            ("view_commento", "Can view commento"),
        )

    autore = models.ForeignKey("anagrafica.Persona", db_index=True, related_name="commenti", on_delete=models.CASCADE)
    commento = models.TextField("Testo del commento")
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True, on_delete=models.SET_NULL, null=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')

    LUNGHEZZA_MASSIMA = 1024


class ConGiudizio():
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


class ConCommenti(models.Model):
    """
    Aggiunge la possibilita' di aggiungere commenti ad
    un oggetto.
    """

    class Meta:
        abstract = True

    commenti = GenericRelation(
        Commento,
        related_query_name='%(class)s',
        content_type_field='oggetto_tipo',
        object_id_field='oggetto_id'
    )

    def commento_notifica_destinatari(self, mittente):
        """
        SOVRASCRIVIMI!
        Ritorna il queryset di persone che devono ricevere
         una notifica ogni volta che un commento viene aggiunto
         da un dato mittente.
        """
        from anagrafica.models import Persona
        return Persona.objects.none()
