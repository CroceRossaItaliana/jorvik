from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from base.tratti import ConMarcaTemporale


class Locazione(ConMarcaTemporale, models.Model):

    class Meta:
        verbose_name = "Locazione Geografica"
        verbose_name_plural = "Locazioni Geografiche"

    objects = models.GeoManager()
    geo = models.PointField(blank=True, default='POINT(0.0 0.0)')
    indirizzo = models.CharField("Indirizzo", max_length=255, blank=True, null=True)


class ConGeolocalizzazione(models.Model):
    """
    Aggiunge le funzioni di geolocalizzazione ad un oggetto.
    """

    class Meta:
        abstract = True

    locazione = models.ForeignKey(Locazione, null=True, blank=True, related_name="%(app_label)s_%(class)s")

    def vicini(self, km):
        """
        Ritorna tutti gli oggetti simili vicini, nei pressi di x KM.
        :param km: Raggio di ricerca in kilometri.
        :return: Una ricerca filtrata.
        """
        if self.locazione is None:
            return self.objects.none()

        self.objects.filter(locazione__geo__distance_lte=(self.locazione.geo, D(km=km)))


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
        return ricerca.filter(locazione__geo__distance_lte=(self.locazione.geo, D(km=self.raggio)))

