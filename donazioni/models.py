from autoslug import AutoSlugField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django_countries.fields import CountryField

from anagrafica.costanti import NAZIONALE
from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.validators import valida_codice_fiscale
from base.models import ModelloSemplice
from base.tratti import ConStorico, ConDelegati, ConMarcaTemporale
from base.utils import TitleCharField, UpperCaseCharField, concept, poco_fa


class Campagna(ModelloSemplice, ConMarcaTemporale, ConStorico, ConDelegati):
    class Meta:
        verbose_name = 'Campagna'
        verbose_name_plural = 'Campagne'
        ordering = ['fine', 'nome', ]
        permissions = (
            ('view_campagna', 'Can view campagna'),
        )

    nome = models.CharField(max_length=255, default='Nuova campagna',
                            db_index=True, help_text='es. Terremoto Centro Italia')
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
        return '/donazioni/campagne/%d/' % (self.pk,)

    @property
    def url_modifica(self):
        return '/donazioni/campagne/%d/modifica' % (self.pk,)

    @property
    def url_aggiungi_donazione(self):
        return '/donazioni/campagne/%d/donazioni/nuova/' % (self.pk,)

    @property
    def url_elenco_donazioni(self):
        return '/donazioni/campagne/%d/donazioni/elenco/' % (self.pk,)

    @property
    def url_cancella(self):
        return '/donazioni/campagne/%d/elimina' % (self.pk,)

    @property
    def link(self):
        return '<a href="%s">%s</a>' % (self.url, self.nome)

    @staticmethod
    def post_save(sender, instance, **kwargs):
        """
        Signal post_save che aggiunge un'etichetta di default alla campagna con lo stesso nome della campagna
        :param sender: classe Campagna
        :param instance: oggetto Campagna
        """
        etichette_correnti = instance.etichette.values_list('nome', flat=True)
        if instance.nome not in etichette_correnti:
            # crea e/o aggiunge etichetta di default
            etichetta, _ = Etichetta.objects.get_or_create(nome=instance.nome,
                                                           comitato=instance.organizzatore,
                                                           default=True)
            instance.etichette.add(etichetta)

    @property
    def url_responsabili(self):
        return '/donazioni/campagne/%d/responsabili/' % (self.pk,)


class Etichetta(ModelloSemplice):
    class Meta:
        verbose_name = 'Etichetta'
        verbose_name_plural = 'Etichette'
        ordering = ['nome', ]
        permissions = (
            ('view_etichetta', 'Can view etichetta'),
        )

    nome = models.CharField(max_length=100, help_text='es. WEB')
    comitato = models.ForeignKey('anagrafica.Sede', related_name='etichette_campagne', on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='nome', always_update=True, max_length=100, unique_with='comitato')
    campagne = models.ManyToManyField(Campagna, related_name='etichette')
    default = models.BooleanField('Etichetta di default', default=False)

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
        :param sedi_qs: le sedi a cui devono 'appartenere' le Etichette.
                        Solitamente, quelle su cui si ha il permesso GESTIONE_CAMPAGNE
        :return: Q object
        """
        filtro = Q(comitato__estensione=NAZIONALE)
        if sedi_qs:
            filtro |= Q(comitato__in=sedi_qs)
        return filtro

    @property
    def url_cancella(self):
        return '/donazioni/etichette/%d/elimina' % (self.pk,)

    @property
    def url_modifica(self):
        return '/donazioni/etichette/%d/modifica' % (self.pk,)

    @property
    def url(self):
        return '/donazioni/etichette/%d/' % (self.pk,)

    @property
    def link(self):
        return '<a href="%s">%s</a>' % (self.url, self.nome)

    @property
    def link_cancella(self):
        return '<a href="%s">%s</a>' % (self.url_cancella, 'X')


class Donatore(ModelloSemplice):
    class Meta:
        verbose_name = 'Donatore'
        verbose_name_plural = 'Donatori'
        permissions = (
            ('view_donatore', 'Can view donatore'),
        )

    nome = TitleCharField('Nome', max_length=64, blank=True)
    cognome = TitleCharField('Cognome', max_length=64, blank=True)
    codice_fiscale = UpperCaseCharField('Codice Fiscale', max_length=16, blank=True,
                                        validators=[valida_codice_fiscale, ])
    email = models.EmailField('Indirizzo e-mail', max_length=64, blank=True)
    data_nascita = models.DateField('Data di nascita', null=True, blank=True)
    comune_nascita = models.CharField('Comune di Nascita', max_length=64, blank=True)
    provincia_nascita = models.CharField('Provincia di Nascita', max_length=2, blank=True)
    stato_nascita = CountryField('Stato di nascita', default='IT')

    ragione_sociale = TitleCharField('Ragione Sociale', max_length=64, blank=True,
                                     help_text='Inserire la ragione sociale nel caso di persona giuridica')

    def __str__(self):
        stringa_output = []
        for f in ('ragione_sociale', 'nome', 'cognome', 'email', 'codice_fiscale'):
            stringa_output.append('{}'.format(getattr(self, f, '')))
        return ' '.join(s for s in stringa_output if s)

    @classmethod
    def _donatore_esistente(cls, **kwargs):
        try:
            istanza = Donatore.objects.get(**kwargs)
        except Donatore.DoesNotExist:
            return
        else:
            return istanza

    @classmethod
    def nuovo_o_esistente(cls, donatore):
        istanza = None
        if donatore.codice_fiscale:
            if not donatore.ragione_sociale:
                istanza = cls._donatore_esistente(codice_fiscale=donatore.codice_fiscale)
            else:
                istanza = cls._donatore_esistente(codice_fiscale=donatore.codice_fiscale,
                                                  ragione_sociale=donatore.ragione_sociale)
            if not istanza and donatore.email:
                istanza = cls._donatore_esistente(email=donatore.email)

        elif donatore.email:
            istanza = cls._donatore_esistente(email=donatore.email)
        elif donatore.nome and donatore.cognome and donatore.data_nascita and donatore.comune_nascita:
            istanza = cls._donatore_esistente(nome=donatore.nome,
                                              cognome=donatore.cognome,
                                              data_nascita=donatore.data_nascita,
                                              comune_nascita=donatore.comune_nascita)
        if not istanza:
            # crea nuovo donatore dai dati derivanti dal modulo ModuloDonatore
            donatore.save()
            return donatore
        # nel caso di donatore esistente, vengono aggiunti nuovi campi se presenti nell'oggetto 'donatore'
        # e non presenti nell'istanza esistente
        istanza = cls._riconcilia_istanze(istanza, donatore)
        return istanza

    @classmethod
    def _riconcilia_istanze(cls, donatore_esistente, donatore_nuovo):
        donatore_campi = {k: v for k, v in donatore_nuovo.__dict__.items() if v}
        for campo, valore in donatore_campi.items():
            valore_donatore_esistente = getattr(donatore_esistente, campo, '')
            # concilia i valori soltanto se il campo del donatore esistente è non presente/vuoto
            if not valore_donatore_esistente:
                setattr(donatore_esistente, campo, valore)
        donatore_esistente.__dict__.update(donatore_campi)
        donatore_esistente.save()
        return donatore_esistente


class Donazione(ModelloSemplice, ConMarcaTemporale):
    CONTANTI = 'C'
    BANCARIA = 'B'
    ONLINE = 'O'
    MODALITA = (
        (CONTANTI, 'Contanti'),
        (BANCARIA, 'Bancaria'),
        (ONLINE, 'Online'),
    )

    class Meta:
        verbose_name = 'Donazione'
        verbose_name_plural = 'Donazioni'
        permissions = (
            ('view_donazione', 'Can view donazione'),
        )

    campagna = models.ForeignKey(Campagna, related_name='donazioni', on_delete=models.PROTECT)
    donatore = models.ForeignKey(Donatore, related_name='donazioni', on_delete=models.CASCADE, null=True)
    importo = models.FloatField('Importo in EUR', default=0.00, help_text='Importo in EUR della donazione')
    modalita = models.CharField('Modalità', blank=True, choices=MODALITA, max_length=1, db_index=True)
    data = models.DateTimeField('Data donazione', help_text='Data donazione', null=True)
    ricorrente = models.BooleanField('Donazione ricorrente', default=False)
    codice_transazione = models.CharField('Codice Transazione', max_length=250, blank=True, null=True,
                                          help_text='Codice univoco che identifica la donazione')

    def __str__(self):
        return '{} {} {}'.format(self.get_modalita_display(), self.importo, self.codice_transazione or '')

    @staticmethod
    def pre_save(sender, instance, **kwargs):
        """
        Signal pre_save che implementa il requisito C-4 per una donazione senza data specificata
        'Per ogni donazione sarà possibile inserire la data della donazione. Ove non
        specificata, questa sarà impostata alla data corrente se la donazione prece-
        dente in ordine temporale è stata fatta in giorni precedenti. Se la donazione
        precedente è stata inserita in data odierna, viene usata la “data donazione” di
        quest’ultima.'
        :param sender: classe Donazione
        :param instance: oggetto Donazione
        """
        if not instance.data:
            try:
                ultima_donazione = Donazione.objects.filter(campagna=instance.campagna).latest('creazione')
            except Donazione.DoesNotExist:
                # prima donazione per la campagna
                instance.data = poco_fa()
            else:
                oggi = timezone.now()
                if (oggi - ultima_donazione.creazione).days >= 1:
                    # ultima donazione aggiunta in giorni precedenti
                    instance.data = poco_fa()
                else:
                    instance.data = ultima_donazione.data


# signals
post_save.connect(Campagna.post_save, Campagna, dispatch_uid='jorvik.donazioni.models.Campagna')
pre_save.connect(Donazione.pre_save, Donazione, dispatch_uid='jorvik.donazioni.models.Donazione')