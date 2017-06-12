from autoslug import AutoSlugField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save

from anagrafica.costanti import NAZIONALE
from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.validators import valida_codice_fiscale
from base.models import ModelloSemplice
from base.tratti import ConStorico, ConDelegati, ConMarcaTemporale
from base.utils import TitleCharField, UpperCaseCharField, concept


class Campagna(ModelloSemplice, ConMarcaTemporale, ConStorico, ConDelegati):

    class Meta:
        verbose_name = 'Campagna'
        verbose_name_plural = 'Campagne'
        ordering = ['fine', 'nome', ]
        permissions = (
            ('view_campagna', 'Can view campagna'),
        )

    nome = models.CharField(max_length=255, default="Nuova campagna",
                            db_index=True, help_text="es. Terremoto Centro Italia")
    organizzatore = models.ForeignKey('anagrafica.Sede', related_name='campagne', on_delete=models.PROTECT)
    descrizione = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    def responsabili_attuali(self):
        return self.delegati_attuali(tipo=RESPONSABILE_CAMPAGNA)

    @property
    def cancellabile(self):
        return not self.donazioni.all().exists()

    @property
    def url(self):
        return "/donazioni/campagne/%d/" % (self.pk,)

    @property
    def url_modifica(self):
        return "/donazioni/campagne/%d/modifica" % (self.pk,)

    @property
    def url_cancella(self):
        return "/donazioni/campagne/%d/elimina" % (self.pk,)

    @property
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url, self.nome)

    @staticmethod
    def post_save(sender, instance, **kwargs):
        """
        Signal post_save che aggiunge un'etichetta di default alla campagna con lo stesso nome della campagna
        :param sender: classe Campagna
        :param instance: oggetto Campagna
        """
        etichette_correnti = instance.etichette.values_list('nome', flat=True)
        if instance.nome not in etichette_correnti:
            # crea e aggiunge etichetta di default
            etichetta, _ = Etichetta.objects.get_or_create(nome=instance.nome,
                                                        comitato=instance.organizzatore,
                                                        default=True)
            instance.etichette.add(etichetta)

    @property
    def url_responsabili(self):
        return "/donazioni/campagne/%d/responsabili/" % (self.pk,)


class Etichetta(ModelloSemplice):
    class Meta:
        verbose_name = 'Etichetta'
        verbose_name_plural = 'Etichette'
        ordering = ['nome', ]
        permissions = (
            ('view_etichetta', 'Can view etichetta'),
        )
    nome = models.CharField(max_length=100, help_text="es. WEB")
    comitato = models.ForeignKey('anagrafica.Sede', related_name='etichette_campagne', on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='nome', always_update=True, max_length=100, unique_with='comitato')
    campagne = models.ManyToManyField(Campagna, related_name='etichette')
    default = models.BooleanField("Etichetta di default", default=False)

    def __str__(self):
        return self.nome

    @classmethod
    @concept
    def query_etichette_comitato(cls, sedi_qs=None):
        """
        Requisiti B-2, B-5.
        Le etichette sono specifiche di un comitato.
        In più, il comitato nazionale può creare delle etichette globali
        visibili a tutti i comitati territoriali
        :param sedi_qs: le sedi a cui devono "appartenere" le Etichette.
                        Solitamente, quelle su cui si ha il permesso GESTIONE_CAMPAGNE
        :return: Q object
        """
        filtro = Q(comitato__estensione=NAZIONALE)
        if sedi_qs:
            filtro |= Q(comitato__in=sedi_qs)
        return filtro

    @property
    def url_cancella(self):
        return "/donazioni/etichette/%d/elimina" % (self.pk,)

    @property
    def url_modifica(self):
        return "/donazioni/etichette/%d/modifica" % (self.pk,)

    @property
    def url(self):
        return "/donazioni/etichette/%d/" % (self.pk,)

    @property
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url, self.nome)

    @property
    def link_cancella(self):
        return "<a href=\"%s\">%s</a>" % (self.url_cancella, 'X')


class Donatore(ModelloSemplice):
    class Meta:
        verbose_name = 'Campagna'
        verbose_name_plural = 'Campagne'
        permissions = (
            ('view_campagna', 'Can view campagna'),
        )
    nome = TitleCharField("Nome", max_length=64, db_index=True)
    cognome = TitleCharField("Cognome", max_length=64, db_index=True)
    codice_fiscale = UpperCaseCharField("Codice Fiscale", max_length=16, blank=False,
                                        unique=True, db_index=True, validators=[valida_codice_fiscale, ])


class Donazione(ModelloSemplice, ConMarcaTemporale):
    campagna = models.ForeignKey(Campagna, related_name='donazioni', on_delete=models.PROTECT)
    donatore = models.ForeignKey(Donatore, related_name='donazioni', on_delete=models.CASCADE)


# signals
post_save.connect(Campagna.post_save, Campagna, dispatch_uid="jorvik.donazioni.models.Campagna")
