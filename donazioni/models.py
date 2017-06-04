from autoslug import AutoSlugField
from django.db import models
from django.db.models.signals import post_save

from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.validators import valida_codice_fiscale
from base.models import ModelloSemplice
from base.tratti import ConStorico, ConDelegati, ConMarcaTemporale
from base.utils import TitleCharField, UpperCaseCharField


class Campagna(ModelloSemplice, ConStorico, ConDelegati):

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

    def aggiungi_responsabile(self, persona):
        self.aggiungi_delegato(RESPONSABILE_CAMPAGNA, persona)

    @property
    def cancellabile(self):
        return not self.donazioni.all().exists()

    @staticmethod
    def post_save(sender, instance, **kwargs):
        """
        Signal post_save che aggiunge un'etichetta alla campagna con lo stesso nome della campagna
        :param sender: classe Campagna
        :param instance: oggetto Campagna
        """
        etichetta = Etichetta(nome=instance.nome, comitato=instance.organizzatore)
        etichetta.save()
        instance.etichette.add(etichetta)


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

    def __str__(self):
        return self.nome


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
