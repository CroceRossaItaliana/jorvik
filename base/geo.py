from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D


class ConGeolocalizzazione(models.Model):
    """
    Aggiunge le funzioni di geolocalizzazione ad un oggetto.
    """

    class Meta:
        abstract = True

    objects = models.GeoManager()
    geo = models.PointField(default='POINT(0.0 0.0)')
    indirizzo = models.CharField("Indirizzo", max_length=255, blank=True, null=True)

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

    raggio = models.FloatField("Raggio KM", default=0.0, null=True, blank=True)

    class Meta:
        abstract = True

    def nel_raggio(self, ricerca):
        """
        Filtra una ricerca, per gli elementi nel raggio di questo elemento.
        :return: La ricerca filtrata
        """
        return ricerca.filter(geo__distance_lte=(self.geo, D(km=self.raggio)))

