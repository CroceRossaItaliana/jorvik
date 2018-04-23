from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr, Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import SET_NULL, F
import googlemaps
from django_countries.fields import CountryField

from base.tratti import ConMarcaTemporale
from django.contrib.gis.measure import Distance, D
from jorvik.settings import GOOGLE_KEY

import logging


logger = logging.getLogger(__name__)


class Locazione(ConMarcaTemporale, models.Model):

    class Meta:
        verbose_name = "Locazione Geografica"
        verbose_name_plural = "Locazioni Geografiche"
        permissions = (
            ("view_locazione", "Can view locazione"),
        )

    indirizzo = models.CharField("Indirizzo", max_length=255, db_index=True)

    objects = models.GeoManager()
    geo = models.PointField(blank=True, default='POINT(0.0 0.0)', db_index=True,
                            spatial_index=True, srid=4326, geography=True)

    via = models.CharField("Via", max_length=64, blank=True)
    civico = models.CharField("Civico", max_length=16, blank=True)
    comune = models.CharField("Comune", max_length=64, blank=True, db_index=True)
    provincia = models.CharField("Provincia", max_length=64, blank=True, db_index=True)
    provincia_breve = models.CharField("Provincia (breve)", max_length=64, blank=True, db_index=True)
    regione = models.CharField("Regione", max_length=64, blank=True, db_index=True)
    cap = models.CharField("CAP", max_length=32, blank=True, db_index=True)
    stato = CountryField("Stato", default="IT")

    def __str__(self):
        return self.indirizzo

    @classmethod
    def scomponi_indirizzo(cls, oggetto):
        INDIRIZZO_PARTI = (
             ('civico',  ('street_number', 'long_name')),
             ('via', ('route', 'long_name')),
             ('comune', ('locality', 'long_name')),
             ('provincia', ('administrative_area_level_2', 'long_name')),
             ('provincia_breve', ('administrative_area_level_2', 'short_name')),
             ('regione', ('administrative_area_level_1', 'long_name')),
             ('stato', ('country', 'short_name')),
             ('cap', ('postal_code', 'long_name'))
        )
        parti = {a[0]: None for a in INDIRIZZO_PARTI}
        for (parte, nomenclatura) in INDIRIZZO_PARTI:
            (a, b) = nomenclatura
            for p in oggetto['address_components']:
                if not a in p['types']:
                    continue
                parti[parte] = p[b].replace('Provincia di ', '').replace('Province of ', '')\
                    .replace('Provincia della ', 'La ').replace('Provincia dell\'', 'L\'')
        return parti

    @classmethod
    def controlla_posizione(cls, coordinate):
        """
        Valida le coordinate. L'unico controllo possibile è che le coordinate non devono essere
        entrambe zero
        :param coordinate: vettore lat / lng ritornato da google geocoding
        :return: coordinate inalterate o '0'
        """
        try:
            if coordinate['lat'] and coordinate['lng']:
                return coordinate
        except (KeyError, ValueError, TypeError):
            return '0'
        return '0'

    @classmethod
    def cerca(cls, indirizzo):
        """
        Usa le API di Google (Geocode) per cercare l'indirizzo,
        ritorna una stringa (indirizzo formattato) per ogni risultato.

        :param indirizzo: Indirizzo da cercare
        :return: Lista di risultati.
        """
        try:
            gmaps = googlemaps.Client(key=GOOGLE_KEY)

        except ValueError:
            # API key not configured
            logger.warning("Chiave API Google non configurata. Le ricerche geografiche non ritorneranno "
                           "alcun risultato.")
            return []

        risultati = gmaps.geocode(indirizzo, region="it", language="it")
        return [
            (x['formatted_address'], cls.controlla_posizione(x['geometry']['location']),
             cls.scomponi_indirizzo(x))
            for x in risultati
        ]

    @classmethod
    def oggetto(self, indirizzo):
        """
        Cerca un oggetto per indirizzo. Se esistente, ritorna
        la referenza. Altrimenti, interroga Google, scompone
        l'indirizzo e ritorna una nuova istanza di Locazione (salvata).
        :param indirizzo: Una stringa da ricercare.
        :return: Oggetto Locazione o None se non trovato.
        """
        if not indirizzo:
            return None

        j = Locazione.objects.filter(indirizzo=indirizzo).first()
        if j:
            return j

        risultati = Locazione.cerca(indirizzo)
        if not len(risultati):
            return None
        risultato = risultati[0]

        j = Locazione.objects.filter(indirizzo=risultato[0]).first()
        if j:
            return j

        l = Locazione(
            indirizzo=risultato[0],
            geo=Point(risultato[1]['lng'], risultato[1]['lat']),
            **{k: risultato[2][k] if risultato[2][k] else '' for k in risultato[2]}
        )
        l.save()
        return l

    def cerca_e_aggiorna(self):
        """
        Cerca indirizzo in 'indirizzo' e aggiorna indirizzo e coordinate.
        """
        risultati = Locazione.cerca(self.indirizzo)
        if not len(risultati):
            return False
        risultato = risultati[0]

        self.indirizzo = risultato[0]
        self.geo = Point(risultato[1]['lng'], risultato[1]['lat'])
        valori = {k: risultato[2][k] if risultato[2][k] else '' for k in risultato[2]}
        for k in valori:
            setattr(self, k, valori[k])
        return self.save()

    @property
    def formattato(self):
        return self.indirizzo.replace("Italy", "Italia")


class ConGeolocalizzazione(models.Model):
    """
    Aggiunge le funzioni di geolocalizzazione ad un oggetto.
    """

    class Meta:
        abstract = True

    locazione = models.ForeignKey(Locazione, null=True, blank=True, related_name="%(app_label)s_%(class)s", on_delete=SET_NULL)

    def post_locazione(self):
        """
        Callback sovrascrivibile. Cosa fare dopo l'impostazione della nuova locazione.
        :return:
        """
        pass

    def imposta_locazione(self, indirizzo):
        """
        Imposta la locazione dell'oggetto dato un indirizzo.
        Se l'indirizzo e' in database, associa e ritorna la referenza
        alla locazione. Altrimenti, cerca con API google, crea nuova
        Locazione, la associa e ne ritorna la referenza. Se nessun
        indirizzo viene trovato, ritorna None.
        :param indirizzo: Indirizzo da cercare e associare.
        :return: Oggetto Locazione o None se non trovato.
        """
        l = Locazione.oggetto(indirizzo)
        if l is None:
            return None
        self.locazione = l
        self.save()
        self.post_locazione()
        return l


    def vicini(self, queryset, km):
        """
        Filtra una QuerySet per tutti gli oggetti simili vicini, nei pressi di x KM.
        :param km: Raggio di ricerca in kilometri.
        :return: Una ricerca filtrata.
        """
        if not self.locazione:
            return queryset.none()

        return queryset.filter(locazione__geo__distance_lte=(self.locazione.geo, Distance(km=km)))

    @property
    def icona_colore(self):
        return 'red'

    def circonferenze_contenenti(self, queryset):
        """
        Dato un queryset di oggetti "ConGeolocalizzazioneRaggio", li filtra
         pescando solo quelli che contengono questo elemento.
        """
        if not self.locazione:
            return queryset.none()

        q = queryset.exclude(locazione__geo__isnull=True).extra(
            where=['ST_DWithin(geo, ST_GeogFromText(%s), raggio*1000)'],
            params=[self.locazione.geo.wkt]
        )
        return q


class ConGeolocalizzazioneRaggio(ConGeolocalizzazione):
    """
    Aggiunge le funzioni di geolocalizzazione e quelle necessarie a rappresentare
    un'area circolare con raggio in kilometri.
    """

    raggio = models.FloatField("Raggio KM", default=0.0, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def nel_raggio(self, ricerca):
        """
        Filtra una ricerca, per gli elementi nel raggio di questo elemento.
        :return: La ricerca filtrata
        """
        if not self.locazione:
            return self.__class__.objects.none()

        q = ricerca.filter(locazione__geo__distance_lte=(self.locazione.geo, D(km=self.raggio)))
        #q = ricerca.filter(locazione__geo__distance_lte=(self.locazione.geo, D(km=self.raggio)))
        #print(q.query)
        return q
