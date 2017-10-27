import itertools

from datetime import timedelta
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q, Sum, Avg, Count
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django_countries.fields import CountryField
from django.conf import settings

from anagrafica.costanti import NAZIONALE
from anagrafica.models import Appartenenza
from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.validators import valida_codice_fiscale, valida_partita_iva
from base.models import ModelloSemplice
from base.stringhe import genera_uuid_casuale
from base.tratti import ConStorico, ConDelegati, ConMarcaTemporale
from base.utils import TitleCharField, UpperCaseCharField, concept, poco_fa, mai
from social.models import ConCommenti
from ufficio_soci.models import Quota


class Campagna(ModelloSemplice, ConMarcaTemporale, ConStorico, ConDelegati):
    class Meta:
        verbose_name = 'Campagna'
        verbose_name_plural = 'Campagne'
        ordering = ['fine', 'nome', ]
        permissions = (
            ('view_campagna', 'Can view campagna'),
        )

    fittizia = models.BooleanField(default=False, help_text='Se True, campagna fittizia per gestire profili di potenziali donatori')
    nome = models.CharField(max_length=255, default='Nuova campagna',
                            db_index=True, help_text='es. Terremoto Centro Italia')
    organizzatore = models.ForeignKey('anagrafica.Sede', related_name='campagne', on_delete=models.PROTECT)
    descrizione = models.TextField(blank=True)
    permetti_scaricamento_ricevute = models.BooleanField(default=True, help_text='Permetti lo scaricamento delle ricevute')
    testo_email_ringraziamento = models.TextField(blank=True,
                                                  help_text="Inserire il testo che sarà incluso nella mail da "
                                                            "inviare ai donatori che hanno fornito l'indirizzo email")

    def __str__(self):
        return self.nome

    @cached_property
    def responsabili_attuali(self):
        return self.delegati_attuali(tipo=RESPONSABILE_CAMPAGNA)

    @cached_property
    def iniziata(self):
        return self.inizio <= poco_fa()

    @cached_property
    def cancellabile(self):
        return not self.donazioni.all().exists()

    @cached_property
    def date_modificabili(self):
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
    def url_importa_da_mailup(self):
        return reverse('donazioni_campagna_importa_mailup', args=(self.pk,))

    @property
    def url_importa_xls(self):
        return reverse('donazioni_campagna_importa', args=(self.pk,))

    @property
    def url_importa_xls_step_1(self):
        return reverse('donazioni_campagna_importa_step_1', args=(self.pk,))

    @property
    def url_importa_xls_step_2(self):
        return reverse('donazioni_campagna_importa_step_2', args=(self.pk,))

    @property
    def url_elenco_donazioni(self):
        return '/donazioni/campagne/%d/donazioni/elenco/' % (self.pk,)

    @property
    def url_elenco_donatori(self):
        return '/donazioni/campagne/%d/donatori/elenco/' % (self.pk,)

    @property
    def url_cancella(self):
        return '/donazioni/campagne/%d/elimina' % (self.pk,)

    @property
    def link(self):
        return '<a href="%s">%s</a>' % (self.url, self.nome)

    @cached_property
    def totale_donazioni(self):
        return self.donazioni.all().aggregate(importo=Sum('importo'))['importo'] or 0

    @cached_property
    def donatori_censiti(self):
        return self.donazioni.filter(donatore__isnull=False).distinct('donatore')

    @staticmethod
    def post_save(sender, instance, **kwargs):
        """
        Signal post_save che aggiunge un'etichetta di default alla campagna con lo stesso nome della campagna
        :param sender: classe Campagna
        :param instance: oggetto Campagna
        """
        if instance.fittizia:
            # non creare le etichette per le campagne fittizie
            return
        slug_etichetta_default = slugify(instance.nome)
        etichette_correnti = instance.etichette.values_list('slug', flat=True)
        if slug_etichetta_default not in etichette_correnti:
            # crea e/o aggiunge etichetta di default
            etichetta = Etichetta(slug=slug_etichetta_default, comitato=instance.organizzatore,
                                  default=True)
            etichetta.save()
            instance.etichette.add(etichetta)

    @property
    def url_responsabili(self):
        return '/donazioni/campagne/%d/responsabili/' % (self.pk,)


class SedeCampagnaFittizia(ModelloSemplice):
    sede = models.ForeignKey('anagrafica.Sede', on_delete=models.PROTECT)
    campagna_fittizia = models.ForeignKey('donazioni.Campagna', on_delete=models.PROTECT)

    @classmethod
    def ottieni_campagna_fittizia(cls, sede=None, campagna=None):
        if not sede and not campagna:
            return None
        if not sede:
            sede = campagna.organizzatore
        associazione_campagna_fittizia = SedeCampagnaFittizia.objects.filter(sede=sede).first()
        if not associazione_campagna_fittizia:
            # ancora non è stata creata una campagna fittizia per la sede organizzatrice
            campagna_fittizia = Campagna(fittizia=True, nome='Campagna fittizia',
                                         descrizione='Campagna fittizia per sede {}'.format(sede),
                                         organizzatore=sede, permetti_scaricamento_ricevute=False,
                                         inizio=poco_fa(), fine=mai())
            campagna_fittizia.save()
            if campagna:
                # aggiungi gli stessi responsabili della campagna passata come argomento
                for responsabile in campagna.responsabili_attuali:
                    campagna_fittizia.aggiungi_delegato(tipo=RESPONSABILE_CAMPAGNA, persona=responsabile)

            associazione_campagna_fittizia = SedeCampagnaFittizia(sede=sede, campagna_fittizia=campagna_fittizia)
            associazione_campagna_fittizia.save()
        return associazione_campagna_fittizia.campagna_fittizia


class Etichetta(ModelloSemplice):
    class Meta:
        verbose_name = 'Etichetta'
        verbose_name_plural = 'Etichette'
        ordering = ['slug', ]
        permissions = (
            ('view_etichetta', 'Can view etichetta'),
        )
        unique_together = ('slug', 'comitato')

    comitato = models.ForeignKey('anagrafica.Sede', related_name='etichette_campagne', on_delete=models.CASCADE)
    slug = models.SlugField(allow_unicode=True, max_length=100, help_text='Questo campo può contenere lettere, numeri e trattini')
    campagne = models.ManyToManyField(Campagna, related_name='etichette')
    default = models.BooleanField('Etichetta di default', default=False)
    donatori = models.ManyToManyField('donazioni.Donatore', related_name='etichette')

    def __str__(self):
        return self.slug

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if Etichetta.objects.filter(slug=self.slug).exists():
            anno_corrente = poco_fa().year
            self.slug = '{}-{}'.format(self.slug, anno_corrente)
            if Etichetta.objects.filter(slug=self.slug).exists():
                orig = self.slug
                for x in itertools.count(1):
                    if not Etichetta.objects.filter(slug=self.slug).exists():
                        break
                    self.slug = '{}-{}'.format(orig, x)
        super().save()

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
        return '<a href="%s">%s</a>' % (self.url, self.slug)


class Donatore(ModelloSemplice, ConCommenti):
    # Scelte tipo donatore
    PRIVATO = 'P'
    AZIENDA = 'A'
    CRI = 'C'
    # Scelte lingua
    ITALIANO = 'IT'
    INGLESE = 'EN'
    FRANCESE = 'FR'
    SPAGNOLO = 'ES'
    TEDESCO = 'DE'
    ARABO = 'AR'
    PORTOGHESE = 'PR'
    CINESE = 'CH'
    GIAPPONESE = 'JA'
    ALTRO = 'OO'
    # Scelte professione
    IMPIEGATO = 'IMP'
    PENSIONATO = 'PENS'
    STUDENTE = 'STUD'
    LIBERO = 'LIBPROF'
    IMPRENDITORE = 'IMPR'
    DIPENDENTE_PUBBLICO = 'PUB'
    ALTRA_PROFESSIONE = 'NN'

    PROFESSIONI = (
        (STUDENTE, 'Studente'),
        (PENSIONATO, 'Pensionato/a'),
        (IMPIEGATO, 'Impiegato/a'),
        (IMPRENDITORE, 'Imprenditore'),
        (LIBERO, 'Libero/a Professionista'),
        (DIPENDENTE_PUBBLICO, 'Dipendente Pubblica Amministrazione'),
        (ALTRA_PROFESSIONE, 'Altra Professione'),
    )

    TIPO_DONATORE = (
        (PRIVATO, 'Privato'),
        (AZIENDA, 'Azienda'),
        (CRI, 'CRI'),
    )
    LINGUE = (
        (ITALIANO, 'Italiano'),
        (INGLESE, 'Inglese'),
        (FRANCESE, 'Francese'),
        (SPAGNOLO, 'Spagnolo'),
        (TEDESCO, 'Tedesco'),
        (PORTOGHESE, 'Portoghese'),
        (GIAPPONESE, 'Giapponese'),
        (CINESE, 'Cinese Mandarino'),
        (ARABO, 'Arabo'),
        (ALTRO, 'Altra lingua non presente'),
    )

    SESSO_DONATORE = (
        ('M', 'Maschile'),
        ('F', 'Femminile'),
    )

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
    partita_iva = models.CharField("Partita IVA", max_length=32, blank=True,
                                   validators=[valida_partita_iva])
    email = models.EmailField('Indirizzo e-mail', max_length=64, blank=True)
    data_nascita = models.DateField('Data di nascita', null=True, blank=True)
    comune_nascita = models.CharField('Comune di Nascita', max_length=64, blank=True)
    provincia_nascita = models.CharField('Provincia di Nascita', max_length=2, blank=True)
    stato_nascita = CountryField('Stato di nascita', blank=True)

    ragione_sociale = TitleCharField('Ragione Sociale', max_length=64, blank=True,
                                     help_text='Inserire la ragione sociale nel caso di persona giuridica')
    tipo_donatore = models.CharField('Tipo Donatore', blank=True, choices=TIPO_DONATORE, max_length=1)
    sesso = models.CharField('Sesso', blank=True, choices=SESSO_DONATORE, max_length=1)
    indirizzo = models.CharField("Indirizzo di residenza", max_length=512, blank=True)
    comune_residenza = models.CharField('Comune di residenza', max_length=64, blank=True)
    provincia_residenza = models.CharField('Provincia di residenza', max_length=2, blank=True)
    stato_residenza = CountryField('Stato di residenza', blank=True)
    cap_residenza = models.CharField('CAP di Residenza', max_length=16, blank=True)
    telefono = models.CharField('Telefono', max_length=64, blank=True)
    cellulare = models.CharField('Cellulare', max_length=64, blank=True)
    fax = models.CharField('FAX', max_length=64, blank=True)
    professione = models.CharField('Professione', blank=True, choices=PROFESSIONI, max_length=10)
    lingua = models.CharField('Lingua', blank=True, choices=LINGUE, max_length=2)
    periodico = models.BooleanField('Donatore periodico', default=False)

    def __str__(self):
        stringa_output = []
        for f in ('ragione_sociale', 'nome', 'cognome'):
            stringa_output.append('{}'.format(getattr(self, f, '')))
        stringa = ' '.join(s for s in stringa_output if s)
        identificativo = self.email or self.codice_fiscale or self.partita_iva or ''
        return '{} {}'.format(stringa, identificativo)

    @cached_property
    def nome_completo(self):
        if self.ragione_sociale:
            return self.ragione_sociale
        if self.nome or self.cognome:
            nome = '{} {}'.format(self.nome, self.cognome).strip()
        else:
            nome = self.email
        return nome

    @property
    def url_modifica(self):
        return '/donazioni/donatore/%d/modifica' % (self.pk,)

    @property
    def url_cancella(self):
        return '/donazioni/donatore/%d/elimina' % (self.pk,)

    @property
    def url(self):
        return '/donazioni/donatore/%d/' % (self.pk,)

    @property
    def url_elenco_donazioni(self):
        return '/donazioni/donatore/%d/donazioni/elenco/' % (self.pk,)

    @classmethod
    def esiste_gia(cls, donatore):
        """
        Metodo che ritorna True se il donatore esiste già in Anagrafica centralizzata
        :param donatore: oggetto Donatore
        :return: (bool, Donatore)
        """
        filtro = None
        if donatore.codice_fiscale:
            filtro = Q(codice_fiscale=donatore.codice_fiscale)
            if donatore.ragione_sociale:
                filtro &= Q(ragione_sociale=donatore.ragione_sociale)
            if donatore.email:
                # se sono presenti entrambi codice_fiscale ed email, utilizzare anche quest'ultima
                # come filtro (in OR)
                filtro |= Q(email=donatore.email)

        elif donatore.email:
            filtro = Q(email=donatore.email)

        elif donatore.nome and donatore.cognome and donatore.data_nascita and donatore.comune_nascita:
            filtro = Q(nome=donatore.nome,
                       cognome=donatore.cognome,
                       data_nascita=donatore.data_nascita,
                       comune_nascita=donatore.comune_nascita)

        istanza_esistente = Donatore.objects.filter(filtro).first() if filtro else None
        return bool(istanza_esistente), istanza_esistente

    @classmethod
    def nuovo_o_esistente(cls, donatore):
        """
        Questo metodo contribuisce ad implementare la logica del requisito C-9:
        'Se sono forniti dati ulteriori dal donatore devono comprendere almeno uno
        tra i seguenti blocchi di informazioni:
            Indirizzo e-mail
            Codice Fiscale (per persone fisiche)
            Nome, Cognome, Data e Luogo di nascita (per persone fisiche)
            Ragione sociale e codice fiscale (per persone giuridiche)
            Nome, Cognome (per persone fisiche)'

        Vedere anche i metodi privati _donatore_esistente e _riconcilia_istanze
        :param donatore: oggetto Donatore
        :return: Record esistente o appena creato
        """
        esiste_gia, istanza = cls.esiste_gia(donatore)
        if not esiste_gia:
            # Non esiste alcun donatore nell'anagrafica donatori centralizzata
            # Crea quindi un nuovo donatore dai dati derivanti dal modulo ModuloDonatore
            donatore.save()
            return donatore

        # nel caso di donatore già esistente, vengono aggiunti nuovi campi se presenti nell'oggetto 'donatore'
        # e non presenti nell'istanza esistente
        # TODO: bisogna inserire un nuovo donatore nel caso alcuni dati non corrispondano
        # (quali indirizzo, telefono etc.)
        # Questo per evitare che dati inseriti per una campagna di un comitato
        # siano visibili ad altri comitati
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

    @cached_property
    def statistiche_donazioni(self):
        res = self.donazioni.all().aggregate(totale=Sum('importo'),
                                             media=Avg('importo'),
                                             totale_donazioni=Count('id'))
        res['media_class'] = 'rosso-scuro' if res['media'] >= settings.SOGLIA_MEDIA_DONAZIONE else ''
        return res

    def commento_notifica_destinatari(self, mittente):
        from anagrafica.models import Persona

        # Come destinatari, sempre i delegati dell'attivita'... tranne me.
        campagne = Campagna.objects.filter(donazioni__in=self.donazioni.all()).distinct()
        destinatari = Persona.objects.none()
        for c in campagne:
            destinatari |= c.responsabili_attuali
        destinatari = destinatari.distinct()
        return destinatari


class Donazione(ModelloSemplice, ConMarcaTemporale):

    # METODI/CANALI DI PAGAMENTO
    CONTANTI = 'C'
    BANCARIA = 'B'
    PAYPAL = 'P'
    AMMADO = 'A'
    AMAZON = 'Z'
    CRI = 'R'
    POSTE = 'O'
    METODO_PAGAMENTO = (
        (CONTANTI, 'Contanti'),
        (CRI, 'CRI.it'),
        (BANCARIA, 'Bancaria'),
        (POSTE, 'Poste'),
        (PAYPAL, 'PayPal'),
        (AMMADO, 'Ammado'),
        (AMAZON, 'Amazon'),
    )
    METODO_PAGAMENTO_REVERSE = {v.lower(): k for k, v in METODO_PAGAMENTO}

    # MODALITA'
    SINGOLA = 'S'
    RICORRENTE = 'R'
    MODALITA = (
        (SINGOLA, 'Singola'),
        (RICORRENTE, 'Ricorrente')
    )

    class Meta:
        verbose_name = 'Donazione'
        verbose_name_plural = 'Donazioni'
        permissions = (
            ('view_donazione', 'Can view donazione'),
        )

    campagna = models.ForeignKey(Campagna, related_name='donazioni', on_delete=models.PROTECT)
    donatore = models.ForeignKey(Donatore, related_name='donazioni', on_delete=models.CASCADE, null=True)
    importo = models.FloatField('Importo in EUR', default=0.00,
                                help_text='Importo in EUR della donazione',
                                validators=[MinValueValidator(0.01,
                                            "L'importo della donazione è al di sotto del minimo consentito")])
    metodo_pagamento = models.CharField('Metodo Pagamento', blank=True, choices=METODO_PAGAMENTO,
                                        max_length=1, db_index=True)
    data = models.DateTimeField('Data donazione', help_text='Data donazione', null=True, db_index=True)
    codice_transazione = models.CharField('Codice Transazione', max_length=250, blank=True, null=True,
                                          help_text='Codice univoco che identifica la donazione')
    permetti_scaricamento_ricevute = models.BooleanField(default=True, help_text='Permetti lo scaricamento della ricevuta')
    modalita_singola_ricorrente = models.CharField('Modalità', blank=True, choices=MODALITA,
                                                   default=SINGOLA,
                                                   help_text='Definisce se una donazione è Singola/Unica o Ricorrente',
                                                   max_length=1, db_index=True)
    email_inviata = models.BooleanField(default=False, help_text='Email di ringraziamento e notifica ricevuta inviata al donatore')

    def __str__(self):
        return '{} {} {}'.format(self.get_metodo_pagamento_display(), self.importo, self.codice_transazione or '')

    @property
    def url_modifica(self):
        return '/donazioni/donazione/%d/modifica' % (self.pk,)

    @property
    def url_ricevuta(self):
        return '/donazioni/donazione/%d/ricevuta' % (self.pk,)

    @property
    def url_invia_notifica(self):
        return '/donazioni/donazione/%d/notifica' % (self.pk,)

    @cached_property
    def con_ricevuta(self):
        """
        La ricevuta è scaricabile soltanto per le donazioni e le campagne che lo permettono
        :return: bool
        """
        return self.permetti_scaricamento_ricevute and self.campagna.permetti_scaricamento_ricevute

    @property
    def url_cancella(self):
        return '/donazioni/donazione/%d/elimina' % (self.pk,)

    @property
    def url(self):
        return '/donazioni/donazione/%d/' % (self.pk,)

    @staticmethod
    def pre_save(sender, instance, **kwargs):
        """
        Signal pre_save che implementa i requisiti
            # C-4 per una donazione senza data specificata
                'Per ogni donazione sarà possibile inserire la data della donazione. Ove non
                specificata, questa sarà impostata alla data corrente se la donazione prece-
                dente in ordine temporale è stata fatta in giorni precedenti. Se la donazione
                precedente è stata inserita in data odierna, viene usata la “data donazione” di
                quest’ultima.'
            # E-10 'Ciascun soggetto donatore sarà associato a tutte le etichette associate alle
                campagne di fundraising a cui ha partecipato come donatore.
            # E-13 'Se un donatore ha almeno una donazione periodica attiva, è marcato come
                "donatore periodico”
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
        if instance.donatore and not instance.campagna.fittizia:
            if instance.modalita_singola_ricorrente == sender.RICORRENTE:
                instance.donatore.periodico = True
                instance.donatore.save()
            for etichetta in instance.campagna.etichette.all():
                instance.donatore.etichette.add(etichetta)

    def ricevuta(self, appartenenza=None):
        """
        """
        filtro = Q(data_versamento=self.data, importo=self.importo,
                   tipo=Quota.RICEVUTA_DONAZIONE, registrato_da=self.campagna.organizzatore.presidente(),
                   )
        if not appartenenza:
            try:
                persona = AssociazioneDonatorePersona.objects.get(donatore=self.donatore).persona
            except AssociazioneDonatorePersona.DoesNotExist:
                return None
            else:
                appartenenza = persona.appartenenze_attuali(
                    sede=self.campagna.organizzatore, membro=Appartenenza.SOGGETTO_DONATORE
                ).first()
        filtro &= Q(appartenenza=appartenenza)
        return Quota.objects.filter(filtro).first() or None


class TokenRegistrazioneDonatore(ModelloSemplice, ConMarcaTemporale):
    class Meta:
        permissions = (
            ("view_token_registrazione_donatore", "Can view token"),
        )
    donatore = models.ForeignKey('donazioni.Donatore', related_name='tokens', on_delete=models.CASCADE)
    sede = models.ForeignKey('anagrafica.Sede', on_delete=models.CASCADE)
    codice = models.CharField(max_length=128, unique=True, db_index=True, null=False)
    redirect = models.CharField(max_length=128, db_index=True, null=True)
    valido_ore = models.IntegerField(default=48)

    def valido(self):
        from django.utils import timezone
        return timezone.now() <= (self.creazione + timedelta(hours=self.valido_ore))

    @classmethod
    def genera(cls, donatore, sede, redirect="/", valido_ore=24):
        """
        Genera un token ai fini della registrazione su GAIA per un donatore economico
        :param sede: la sede organizzatrice della campagna a cui il donatore ha partecipato
        :param redirect:
        :param donatore: Oggetto Donatore
        :param valido_ore:
        :return:
        """
        codice = genera_uuid_casuale()
        t = cls(
            donatore=donatore,
            sede=sede,
            codice=codice,
            valido_ore=valido_ore,
            redirect=redirect,
        )
        t.save()
        return codice

    @property
    def url(self):
        return "/token-donatore/%s/" % (self.codice,)

    @classmethod
    def verifica(cls, token):
        """
        Verifica se un token e' valido per una data persona.

        """
        try:
            token = cls.objects.get(codice=token)
            if token.valido():
                return token.donatore, token.redirect
            else:
                return False
        except cls.DoesNotExist:
            return False


class AssociazioneDonatorePersona(ModelloSemplice):
    class Meta:
        verbose_name = 'Associazione Donatore Persona'
        verbose_name_plural = 'Associazioni Donatore Persona'
        permissions = (
            ('view_associazione_donatore_persona', 'Can view associazione donatore persona'),
        )
    donatore = models.ForeignKey('donazioni.Donatore', on_delete=models.CASCADE)
    persona = models.ForeignKey('anagrafica.Persona', on_delete=models.CASCADE)


# signals
post_save.connect(Campagna.post_save, Campagna, dispatch_uid='jorvik.donazioni.models.Campagna')
pre_save.connect(Donazione.pre_save, Donazione, dispatch_uid='jorvik.donazioni.models.Donazione')
