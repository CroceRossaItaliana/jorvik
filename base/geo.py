from django.contrib.gis.db import models
from django.contrib.gis.measure import D


class ConGeolocalizzazione(models.Model):
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


class ConGeolocalizzazioneRaggio(ConGeolocalizzazione):
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

