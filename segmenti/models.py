from django.db import models
from django.utils import six

from anagrafica.costanti import TERRITORIALE
from anagrafica.models import Sede, Persona
from .segmenti import SEGMENTI, NOMI_SEGMENTI


class FiltroSegmentoQuerySet(models.QuerySet):
    """
    QuerySet dedicato ai segmenti
    """

    def oggetti_collegati(self):
        campo = '{}_id'.format(self.model._oggetto_collegato.__name__.lower())
        vals = self.values_list(campo, flat=True)
        return self.model._oggetto_collegato.objects.filter(
            models.Q(segmenti__isnull=True) |
            models.Q(pk__in=vals)
        ).distinct()

    def _get_filtri(self, segmenti):
        filtri = models.Q(pk=None)
        for filtro_attivo in segmenti:
            filtri |= models.Q(**filtro_attivo)
        return filtri

    def filtra_per_segmenti(self, utente):
        """
        Filtra il QuerySet in base  in base ai segmenti di appartenenza dell'utente
        compresi i filtri sulle sedi e sui titoli

        :param utente: Utente su cui filtrare gli oggetti
        :return: Queryset filtrato
        """
        filtri = self._get_filtri(utente.segmenti_collegati)
        return self.filter(filtri)


class BaseSegmentoBase(models.base.ModelBase):
    """
    Metaclasse per aggiungere automaticamente la ForeignKey al modello collegato.

    Questo permette di gestire gli automatismi in FiltroSegmentoQuerySet
    """
    def __new__(cls, name, bases, attrs):
        # create a new class (using the super-metaclass)
        modello_collegato = attrs['_oggetto_collegato']
        if modello_collegato:
            nome_campo = modello_collegato.__name__.lower()
            attrs[nome_campo] = models.ForeignKey(modello_collegato, related_name='segmenti')
            attrs['objects'] = FiltroSegmentoQuerySet.as_manager()
        new_class = super(BaseSegmentoBase, cls).__new__(cls, name, bases, attrs)
        return new_class


class BaseSegmento(six.with_metaclass(BaseSegmentoBase, models.Model)):

    LIMITED_CHOICES = {
        'tipo': Sede.COMITATO
    }

    segmento = models.CharField(max_length=256, choices=NOMI_SEGMENTI)
    titolo = models.ForeignKey(
        "curriculum.Titolo", blank=True, null=True,
        help_text='Usato solo con il segmento \'Volontari aventi un dato titolo\''
    )
    sede = models.ForeignKey(Sede, blank=True, null=True, limit_choices_to=LIMITED_CHOICES,)
    sedi_sottostanti = models.BooleanField(default=False, db_index=True,
                                       help_text="Se selezionato, il segmento viene applicato utilizzando la sede "
                                                 "selezionata e le sedi sottostanti.")

    _metodo = None
    _oggetto_collegato = None

    class Meta:
        abstract = True
        verbose_name = 'segmento'
        verbose_name_plural = 'segmenti'

    def __str__(self):
        return '{0} - {1}'.format(self.get_segmento_display(), self.pk)

    def filtro(self):
        if not self._metodo:
            self._metodo = SEGMENTI.get(self.segmento)
        return self._metodo

    def get_extra_filters(self):
        filters = {}
        if self.titolo:
            filters['titoli_personali__titolo'] = self.titolo.pk
        if self.sede:
            if self.sedi_sottostanti:
                filters['appartenenze__sede__in'] = self.sede.espandi(includi_me=True, pubblici=True)
            else:
                filters['appartenenze__sede'] = self.sede.pk

        return filters

