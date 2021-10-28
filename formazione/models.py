import re
import datetime
import time
import uuid

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Q
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from anagrafica.models import Sede, Persona, Appartenenza, Delega
from anagrafica.costanti import PROVINCIALE, TERRITORIALE, LOCALE, REGIONALE, NAZIONALE
from anagrafica.validators import valida_dimensione_file_8mb, valida_dimensione_file_6mb
from anagrafica.permessi.applicazioni import (DIRETTORE_CORSO, OBIETTIVI, PRESIDENTE, COMMISSARIO)
from anagrafica.validators import (valida_dimensione_file_8mb, ValidateFileSize)
from anagrafica.permessi.applicazioni import (DIRETTORE_CORSO, OBIETTIVI, PRESIDENTE, COMMISSARIO, RESPONSABILE_EVENTO)
from anagrafica.permessi.incarichi import (INCARICO_ASPIRANTE, INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI)
from anagrafica.permessi.costanti import MODIFICA
from base.files import PDF, Zip
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.utils import concept, poco_fa
from base.tratti import ConMarcaTemporale, ConDelegati, ConStorico, ConPDF
from base.models import ConAutorizzazioni, ConVecchioID, Autorizzazione, ModelloSemplice
from base.errori import messaggio_generico
from curriculum.models import Titolo
from curriculum.areas import OBBIETTIVI_STRATEGICI
from jorvik.settings import FORMAZIONE_MASSMAIL_CHUNK, FORMAZIONE_MASSMAIL_SLEEP
from posta.models import Messaggio
from social.models import ConCommenti, ConGiudizio
from survey.models import Survey
from .tasks import task_invia_email_apertura_evento
from .training_api import TrainingApi
from .validators import (course_file_directory_path, validate_file_extension,
                         delibera_file_upload_path, evento_file_directory_path)
import logging

logger = logging.getLogger(__name__)

class Evento(ModelloSemplice, ConDelegati, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti):
    PREPARAZIONE = 'P'
    ATTIVO = 'A'
    ANNULLATO = 'X'
    TERMINATO = 'T'

    STATO = (
        (PREPARAZIONE, 'In preparazione'),
        (ATTIVO, 'Attivo'),
        (TERMINATO, 'Terminato'),
        (ANNULLATO, 'Annullato'),
    )

    nome = models.CharField(max_length=200)
    data_inizio = models.DateTimeField(blank=False, null=False)
    data_fine = models.DateTimeField(blank=False, null=False)
    sede = models.ForeignKey(Sede, help_text="La Sede organizzatrice dell'Evento.")
    stato = models.CharField('Stato', choices=STATO, max_length=1, default=PREPARAZIONE)
    descrizione = models.TextField(blank=True, null=True)

    def __str__(self):
        return '%s' % self.nome

    @property
    def url_responsabile(self):
        return reverse('formazione:responsabile_evento', args=[self.pk])

    @property
    def url_position(self):
        return reverse('evento:position_change', args=[self.pk])

    @property
    def url_modifica(self):
        return reverse('evento:modifica', args=[self.pk])

    @property
    def url(self):
        return reverse('evento:info', args=[self.pk])

    @property
    def link(self):
        return '<a href="%s">%s</a>' % (self.url, self.nome)

    @property
    def url_attiva(self):
        return reverse('evento:attiva', args=[self.pk])

    @property
    def url_annulla(self):
        return reverse('evento:annulla', args=[self.pk])

    @property
    def url_termina(self):
        return reverse('evento:termina', args=[self.pk])

    @property
    def ha_posizione(self):
        return True if self.locazione else False

    @property
    def url_mappa(self):
        return reverse('evento:mappa', args=[self.pk])

    @property
    def attivabile(self):
        if self.stato == self.PREPARAZIONE and self.locazione:
            corsi = self.corsi_associati

            if corsi:
                return False not in [corso.stato == Corso.ATTIVO for corso in corsi]
            else:
                return False

        return False

    def attiva(self, rispondi_a=None):
        if self.attivabile:
            if self.ha_posizione:
                self.stato = self.ATTIVO

                task_invia_email_apertura_evento.apply_async(args=(self.pk, rispondi_a.pk),)

                self.save()

                if self.sede.estensione == TERRITORIALE:
                    destinatari = [self.sede.sede_regionale.presidente()]
                    destinatari.extend(self.sede.sede_regionale.delegati_formazione())
                    Messaggio.costruisci_e_accoda(
                        oggetto="Attivazione Evento {}".format(self),
                        modello="email_attivazione_evento_presidente_delegati_fomazioni.html",
                        corpo={
                            "evento": self
                        },
                        destinatari=destinatari,
                    )
                elif self.sede.estensione == REGIONALE:
                    Messaggio.invia_raw(
                        oggetto="Attivazione Evento {}".format(self),
                        corpo_html=get_template(
                            'email_attivazione_evento_presidente_delegati_fomazioni.html'
                        ).render({"evento": self}),
                        email_mittente=Messaggio.NOREPLY_EMAIL,
                        lista_email_destinatari=['formazione@cri.it', ],
                    )

                return self.url
            else:
                return self.url_position

    def referenti_evento(self):
        oggetto_tipo = ContentType.objects.get_for_model(self)
        deleghe = Delega.objects.filter(tipo=RESPONSABILE_EVENTO,
                                        oggetto_tipo=oggetto_tipo.pk,
                                        oggetto_id=self.pk)
        return deleghe

    def _invia_email_volotari(self, rispondi_a=None):
        # Tutti i corsi sono aperti per la stessa lista di volontari/dipendenti
        corso = self.corsi_associati.first()

        for queryset in corso._corso_activation_recipients_for_email_generator():
            oggetto = "Evento Formazione: {}".format(self)

            for recipient in queryset:
                email_data = dict(
                    oggetto=oggetto,
                    modello="email_attivazione_evento_volontari.html",
                    corpo={
                        'persona': recipient,
                        'evento': self,
                    },
                    destinatari=[recipient],
                    rispondi_a=rispondi_a
                )

                Messaggio.costruisci_e_accoda(**email_data)

            time.sleep(FORMAZIONE_MASSMAIL_SLEEP)

    @property
    def annullabile(self):
        if self.stato == self.PREPARAZIONE or self.stato == self.ATTIVO:
            corsi = self.corsi_associati
            if corsi:
                # se tutti i corsi sono in attivo/preparazione e non ci sono lezioni iniziate
                return False not in [
                    (corso.stato == Corso.PREPARAZIONE or corso.stato == Corso.ATTIVO) and
                    not corso.lezioni.filter(inizio__lte=datetime.datetime.now()).exists() for corso in corsi
                ]
            else:
                return True
        return False

    @property
    def terminabile(self):
        if self.stato == self.ATTIVO:
            corsi = self.corsi_associati
            if corsi:
                return False not in [corso.stato == Corso.TERMINATO or corso.stato == Corso.ANNULLATO for corso in corsi]
            else:
                return False
        return False

    def termina(self):
        self.stato = self.TERMINATO
        self.save()
        return reverse('formazione:evento_elenco')

    def annulla(self, persona):
        self.stato = self.ANNULLATO
        corsi = self.corsi_associati
        for corso in corsi:
            corso.annulla(persona)
        self.save()
        return reverse('formazione:evento_elenco')

    @property
    def corsi_associati(self):
        return CorsoBase.objects.filter(evento=self)

    @property
    def totale_corsi(self):
        return CorsoBase.objects.filter(evento=self)

    @property
    def corsi_attivi(self):
        return CorsoBase.objects.filter(evento=self, stato=Corso.ATTIVO)

    @property
    def corsi_terminati(self):
        return CorsoBase.objects.filter(evento=self, stato=Corso.TERMINATO)

    @property
    def get_evento_links(self):
        return self.eventolink_set.filter(is_enabled=True)

    @property
    def get_evento_files(self):
        return self.eventofile_set.filter(is_enabled=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventi'


class Corso(ModelloSemplice, ConDelegati, ConMarcaTemporale,
            ConGeolocalizzazione, ConCommenti, ConGiudizio):
    # Tipologia di corso
    CORSO_NUOVO = 'C1'
    BASE = 'BA'
    BASE_ONLINE = 'BO'
    CORSO_ONLINE = 'CO'
    CORSO_EQUIPOLLENZA = 'CE'
    TIPO_CHOICES = (
        (BASE, 'Corso di Formazione per Volontari CRI'),
        (BASE_ONLINE, 'Corso di Formazione per Volontari CRI Online'),
        (CORSO_NUOVO, 'Altri Corsi'),
        (CORSO_ONLINE, 'Corsi online'),
        (CORSO_EQUIPOLLENZA, 'Corsi equipollenza'),
    )

    # Stato del corso
    PREPARAZIONE = 'P'
    ATTIVO = 'A'
    ANNULLATO = 'X'
    TERMINATO = 'T'  # TODO Terminare il corso automaticamente!
    STATO = (
        (PREPARAZIONE, 'In preparazione'),
        (ATTIVO, 'Attivo'),
        (TERMINATO, 'Terminato'),
        (ANNULLATO, 'Annullato'),
    )
    stato = models.CharField('Stato', choices=STATO, max_length=1, default=PREPARAZIONE)
    sede = models.ForeignKey(Sede, related_query_name='%(class)s_corso',
                             help_text="La Sede organizzatrice del Corso.")
    tipo = models.CharField('Tipo', max_length=4, choices=TIPO_CHOICES, blank=True)

    class Meta:
        abstract = True
        permissions = (
            ("view_corso", "Can view corso"),
        )

    @property
    def is_base(self):
        return self.tipo != self.BASE


class CorsoFile(models.Model):
    is_enabled = models.BooleanField(default=True)
    corso = models.ForeignKey('CorsoBase')
    file = models.FileField('FIle', null=True, blank=True,
        upload_to=course_file_directory_path,
        validators=[valida_dimensione_file_8mb, validate_file_extension],
        # help_text="Formati dei file supportati: doc, xls, pdf, zip, "
        #     "jpg (max 8mb))",
    )
    download_count = models.PositiveIntegerField(default=0)

    def download_url(self):
        reverse_url = reverse('courses:materiale_didattico_download', args=[self.corso.pk])
        return reverse_url + "?id=%s" % self.pk

    def filename(self):
        import os
        return os.path.basename(self.file.name)

    def __str__(self):
        file = self.file if self.file else ''
        corso = self.corso if hasattr(self, 'corso') else ''
        return '<%s> of %s' % (file, corso)


class EventoFile(models.Model):
    is_enabled = models.BooleanField(default=True)
    evento = models.ForeignKey('Evento')
    file = models.FileField(
        'File',
        null=True,
        blank=True,
        upload_to=evento_file_directory_path,
        validators=[valida_dimensione_file_8mb, validate_file_extension],
    )
    download_count = models.PositiveIntegerField(default=0)

    def download_url(self):
        reverse_url = reverse('evento:evento_file', args=[self.evento.pk])
        return reverse_url + "?id=%s" % self.pk

    def filename(self):
        import os
        return os.path.basename(self.file.name)

    def __str__(self):
        file = self.file if self.file else ''
        evento = self.evento if hasattr(self, 'evento') else ''
        return '<%s> of %s' % (file, evento)


class CorsoLink(models.Model):
    is_enabled = models.BooleanField(default=True)
    corso = models.ForeignKey('CorsoBase')
    link = models.URLField('Link', null=True, blank=True)

    def __str__(self):
        corso = self.corso if hasattr(self, 'corso') else ''
        return '<%s> of %s' % (self.link, corso)


class EventoLink(models.Model):
    is_enabled = models.BooleanField(default=True)
    evento = models.ForeignKey('Evento')
    link = models.URLField('Link', null=True, blank=True)

    def __str__(self):
        evento = self.evento if hasattr(self, 'evento') else ''
        return '<%s> of %s' % (self.link, evento)


class CorsoBase(Corso, ConVecchioID, ConPDF):
    from django.core.validators import MinValueValidator

    MIN_PARTECIPANTI = 10
    MAX_PARTECIPANTI = 30

    EXT_MIA_SEDE        = '1'
    EXT_LVL_REGIONALE   = '2'
    EXTENSION_TYPE_CHOICES = [
        (EXT_MIA_SEDE, "Solo su mia sede di appartenenza"),
        (EXT_LVL_REGIONALE, "A livello regionale"),
    ]

    data_inizio = models.DateTimeField(blank=False, null=False,
        help_text="La data di inizio del corso. Utilizzata per la gestione delle iscrizioni.")
    data_esame = models.DateTimeField(blank=False, null=False)
    data_esame_2 = models.DateTimeField(_('Seconda data esame'), blank=True, null=True)
    data_esame_pratica = models.DateTimeField(_('Data esame pratica'), blank=True, null=True)

    progressivo = models.SmallIntegerField(blank=False, null=False, db_index=True)
    anno = models.SmallIntegerField(blank=False, null=False, db_index=True)
    descrizione = models.TextField(blank=True, null=True)

    data_attivazione = models.DateField(blank=True, null=True)
    data_convocazione = models.DateField(blank=True, null=True)
    op_attivazione = models.CharField('Ordinanza presidenziale attivazione',
                                        max_length=255, blank=True, null=True)
    op_convocazione = models.CharField('Ordinanza presidenziale convocazione',
                                        max_length=255, blank=True, null=True)
    extension_type = models.CharField(max_length=5, blank=True, null=True,
                                      default=EXT_MIA_SEDE,
                                      choices=EXTENSION_TYPE_CHOICES)
    min_participants = models.SmallIntegerField("Minimo partecipanti",
        default=MIN_PARTECIPANTI,
        validators=[MinValueValidator(MIN_PARTECIPANTI)])
    max_participants = models.SmallIntegerField("Massimo partecipanti",
                                                default=MAX_PARTECIPANTI)
    delibera_file = models.FileField('Delibera', null=True,
        upload_to=delibera_file_upload_path,
        validators=[valida_dimensione_file_6mb, validate_file_extension]
    )
    commissione_esame_file = models.FileField('Commissione esame delibera',
        null=True, blank=True, upload_to='courses/commissione_esame')
    commissione_esame_names = models.CharField(_('Commissione esame nomi'),
        max_length=255, null=True, blank=True)
    titolo_cri = models.ForeignKey(Titolo, blank=True, null=True,
                                   verbose_name="Titolo CRI")
    cdf_level = models.CharField(max_length=3, choices=Titolo.CDF_LIVELLI,
                                 null=True, blank=True)
    cdf_area = models.CharField(max_length=3, choices=OBBIETTIVI_STRATEGICI,
                                 null=True, blank=True)
    survey = models.ForeignKey(Survey, blank=True, null=True,
                               verbose_name='Questionario di gradimento')

    evento = models.ForeignKey(Evento, blank=True, null=True)

    PUOI_ISCRIVERTI_OK = "IS"
    PUOI_ISCRIVERTI = (PUOI_ISCRIVERTI_OK,)

    SEI_ISCRITTO_PUOI_RITIRARTI = "GIA"
    SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI = "IPC"
    SEI_ISCRITTO_NON_PUOI_RITIRARTI = "NP"
    SEI_ISCRITTO = (SEI_ISCRITTO_PUOI_RITIRARTI,
                    SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI,)

    NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO = "VOL"
    NON_PUOI_ISCRIVERTI_ESTENSIONI_NON_COINCIDONO = "ENC"
    NON_PUOI_ISCRIVERTI_TROPPO_TARDI = "TAR"
    NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO = "ALT"
    NON_PUOI_SEI_ASPIRANTE = 'ASP'
    NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI = 'NHT'
    NON_HAI_CARICATO_DOCUMENTI_PERSONALI = 'NHCDP'
    NON_HAI_DOCUMENTO_PERSONALE_VALIDO = 'NHDPV'
    NON_PUOI_ISCRIVERTI = (NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO,
                           NON_PUOI_ISCRIVERTI_TROPPO_TARDI,
                           # NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO,
                           NON_PUOI_ISCRIVERTI_ESTENSIONI_NON_COINCIDONO,
                           NON_PUOI_SEI_ASPIRANTE,
                           NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI,
                           NON_HAI_CARICATO_DOCUMENTI_PERSONALI,
                           NON_HAI_DOCUMENTO_PERSONALE_VALIDO)

    NON_PUOI_ISCRIVERTI_SOLO_SE_IN_AUTONOMIA = (NON_PUOI_ISCRIVERTI_TROPPO_TARDI,)

    @property
    def annullabile(self):
        if self.stato == self.PREPARAZIONE or self.stato == self.ATTIVO:
            if not self.lezioni.filter(inizio__lte=datetime.datetime.now()).exists():
                return True
        return False

    def persona(self, persona):
        # Validazione per Nuovi Corsi (Altri Corsi)
        if self.is_nuovo_corso or self.online:
            # Aspirante non può iscriversi a corso nuovo
            if persona.ha_aspirante:
                return self.NON_PUOI_SEI_ASPIRANTE

        # Non fare la verifica per gli aspiranti (non hanno appartenenze)
        if not persona.ha_aspirante:
            if not self.is_nuovo_corso and not self.online and persona.volontario:
                return self.NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO

            # Controllo estensioni
            if self.extension_type in [CorsoBase.EXT_MIA_SEDE, CorsoBase.EXT_LVL_REGIONALE]:
                if not self.persona_verifica_estensioni(persona):
                    return self.NON_PUOI_ISCRIVERTI_ESTENSIONI_NON_COINCIDONO

        # if not persona.has_required_titles_for_course(course=self):
        #     return self.NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI

        # Verifica presenza dei documenti personali aggiornati
        if persona.personal_identity_documents():
            esito_verifica = self.persona_verifica_documenti_personali(persona)
            if esito_verifica:
                return esito_verifica
        else:
            return self.NON_HAI_CARICATO_DOCUMENTI_PERSONALI

        # UPDATE: (GAIA-93) togliere blocco che non può iscriversi a più corsi
        # if PartecipazioneCorsoBase.con_esito_ok(persona=persona,
        #                                         corso__tipo=self.BASE,
        #                                         corso__stato=self.ATTIVO).exclude(corso=self).exists():
        #     return self.NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO

        # Controlla se già iscritto.
        if PartecipazioneCorsoBase.con_esito_pending(persona=persona, corso=self).exists():
            return self.SEI_ISCRITTO_PUOI_RITIRARTI

        if PartecipazioneCorsoBase.con_esito_ok(persona=persona, corso=self).exists():
            # UPDATE: (GAIA-93) utente può ritirarsi dal corso in qualsiasi momento.
            return self.SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI

        if self.troppo_tardi_per_iscriverti:
            return self.NON_PUOI_ISCRIVERTI_TROPPO_TARDI

        if not persona.personal_identity_documents():
            return self.NON_HAI_CARICATO_DOCUMENTI_PERSONALI

        if persona.personal_identity_documents():
            today = datetime.datetime.now().date()
            documents = persona.personal_identity_documents()
            gt_exists = documents.filter(expires__gt=today).exists()
            lt_exists = documents.filter(expires__lt=today).exists()

            if lt_exists and not gt_exists:
                return self.NON_HAI_DOCUMENTO_PERSONALE_VALIDO

        return self.PUOI_ISCRIVERTI_OK

    def persona_verifica_documenti_personali(self, persona):
        documents = persona.personal_identity_documents()
        today = datetime.datetime.now().date()
        gt_exists = documents.filter(expires__gt=today).exists()
        lt_exists = documents.filter(expires__lt=today).exists()

        if lt_exists and not gt_exists:
            return self.NON_HAI_DOCUMENTO_PERSONALE_VALIDO

    def persona_verifica_estensioni(self, persona):
        # Prendere le appartenenze | sede dell'utente
        persona_appartenenze = persona.appartenenze_attuali()

        # Prendere le estensioni del corso
        estensioni_dict = dict()

        def esplora_sede(sede, estensione=None, idx=1):
            con_sottosedi = sede.esplora()
            sede_sottosedi = list(con_sottosedi.values_list('id', flat=True))
            if idx not in estensioni_dict:
                estensioni_dict[idx] = {
                    'sede_sottosedi': sede_sottosedi,
                    'segmenti': estensione.segmento if estensione else None,
                    'estensione': estensione if estensione else None
                }
            else:
                estensioni_dict[idx]['sede_sottosedi'].extend(sede_sottosedi)

        if self.extension_type == CorsoBase.EXT_MIA_SEDE:
            # Se l'mpostazione è: Solo si mia sede di appartenenze
            esplora_sede(self.sede)
        else:
            # Se l'mpostazione è: A livello regionale
            for idx, estensione in enumerate(self.get_extensions(), 1):
                # Leggere le impostazioni di ogni estensione
                for sede in estensione.sede.all():
                    esplora_sede(sede, estensione, idx)

        # Incrociare le sedi delle appartenenze dell'Utente e del Corso
        appartenenze_che_coincidono = Appartenenza.objects.none()

        for k,v in estensioni_dict.items():
            segmenti, sedi = v['segmenti'], v['sede_sottosedi']

            q = persona_appartenenze.filter(sede__in=sedi)

            # Segmenti vuoto nel caso di estensione mia sede
            # perchè li i segmenti non si selezionano
            if segmenti is not None:
                q.filter(membro__in=segmenti)

            appartenenze_che_coincidono |= q

        if appartenenze_che_coincidono.exists():
            # Una delle sedi di appartenenze dell'Utente si è trovata fra le
            # sedi delle impostazioni delle estensioni del corso
            return True

        return False

    def possibili_destinazioni(self):
        """ Ritorna le possibili destinazioni per l'iscrizione dei Volontari."""
        return self.sede.comitato.espandi(includi_me=True)

    @property
    def online(self):
        return self.tipo == self.CORSO_ONLINE

    @property
    def moodle(self):
        return self.titolo_cri.moodle

    @property
    def prossimo(self):
        """
        Ritorna True il corso e' prossimo (inizia tra meno di due settimane).
        """
        return (
            poco_fa() <= self.data_inizio <= (poco_fa() + datetime.timedelta(15))
        )

    @classmethod
    @concept
    def pubblici(cls):
        """ Concept per Corsi pubblici (attivi e non ancora iniziati...) """
        return Q(stato=cls.ATTIVO,
            data_inizio__gte=timezone.now() - datetime.timedelta(
                days=settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI
            ))

    @classmethod
    def find_courses_for_volunteer(cls, volunteer, sede, evento=True):
        today = now().today()

        if not sede:
            return cls.objects.none()  # corsi non trovati perchè utente non ha sede

        ###
        # Trova corsi che hanno <sede> uguale alla <sede del volontario>
        ###
        qs_estensioni_1 = CorsoEstensione.objects.filter(sede__in=sede,
                                                         corso__tipo__in=[
                                                             Corso.CORSO_NUOVO,
                                                             Corso.CORSO_ONLINE,
                                                             Corso.BASE,
                                                             Corso.CORSO_EQUIPOLLENZA
                                                         ],
                                                         corso__stato=Corso.ATTIVO)
        courses_1 = cls.objects.filter(id__in=qs_estensioni_1.values_list('corso__id'))

        ###
        # Trova corsi dove la <sede del volontario> si verifica come sede sottostante
        ###
        # four_weeks_delta = today + datetime.timedelta(weeks=4)
        qs_estensioni_2 = CorsoEstensione.objects.filter(
            corso__tipo__in=[Corso.CORSO_NUOVO, Corso.CORSO_ONLINE, Corso.BASE, Corso.CORSO_EQUIPOLLENZA],
            corso__stato=Corso.ATTIVO,
        ).exclude(corso__id__in=courses_1.values_list('id', flat=True))

        ###
        # Questo loop cerca coincidenza della sede dell'utente fra le sedi/sottosedi
        # delle estensioni selezionati sopra.
        ###
        courses_2 = list()
        for estensione in qs_estensioni_2:
            for s in estensione.sede.all():
                sedi_sottostanti = s.esplora()
                for _ in sede:
                    if _ in sedi_sottostanti:
                        # Prendo il corso di ogni estensione dove si è verificata la sede
                        _corso = estensione.corso
                        if _corso not in courses_2:
                            courses_2.append(_corso.pk)

        courses_2 = cls.objects.filter(id__in=courses_2)

        ###
        # Filtra corsi per: segmento e le <Appartenenza> dell'utente
        ###
        q_segmento_objects = Q()
        appartenenze = volunteer.appartenenze_attuali().values_list('membro', flat=True)
        for appartenenza in appartenenze:
            q_segmento_objects.add(Q(segmento__icontains=appartenenza), Q.OR)

        ###
        # Filtra corsi per: segmento_volontario e le <Delega> dell'utente
        # TODO: per il momento non serve (GAIA-116/32)
        ###
        # q_segmento_volontario_objects = Q()
        # deleghe = volunteer.deleghe_attuali().filter(tipo__in=[PRESIDENTE, COMMISSARIO] + list(OBIETTIVI.values())).values_list('tipo', flat=True)
        # for delega in deleghe:
        #     replaced_value = None
        #     if delega in [PRESIDENTE, COMMISSARIO]:
        #         replaced_value = CorsoEstensione.PRESIDENTI_COMMISSARI
        #     elif delega in OBIETTIVI.values():
        #         replaced_value = CorsoEstensione.DELEGATI_TECNICI
        #
        #     if replaced_value:
        #         q_segmento_volontario_objects.add(Q(segmento_volontario__icontains=replaced_value), Q.OR)

        ###
        # Prepara condizioni per filtrare estensioni per segmenti per volontari maggiorenni/giovani
        # TODO: per il momento non serve (GAIA-116/32)
        ###
        # q_volontario_years = None
        # years_today = datetime.datetime.now() - relativedelta(years=volunteer.data_nascita.year)
        # years_today = years_today.year
        # if years_today > 18:
        #     q_volontario_years = CorsoEstensione.VOLONTARI_MAGGIORENNI
        # elif years_today <= 33:
        #     q_volontario_years = CorsoEstensione.VOLONTARI_GIOVANI

        ###
        # Filtra estensioni (finalmente)
        ###
        collected_estensioni = qs_estensioni_1 | qs_estensioni_2
        collected_estensioni = collected_estensioni.filter(q_segmento_objects)

        ###
        # Ricerca corsi per estensioni filtrate
        ###
        collected_courses_by_sede = courses_1 | courses_2

        return collected_courses_by_sede.filter(id__in=collected_estensioni.values_list('corso', flat=True))

    # @classmethod
    # def find_courses_for_volunteer(cls, volunteer):
    #     """
    #     Questo metodo è stato commentato perchè nel task GAIA-97 è stato
    #     chiesto di togliere i requisiti necessari per partecipare ai corsi
    #     (quindi anche per rendere i corsi trovabili/visualizzabili in ricerca).
    #     Il metodo sostituitivo è descritto sopra.
    #     """
    #
    #     sede = volunteer.sedi_attuali(membro=Appartenenza.VOLONTARIO)
    #     if sede:
    #         sede = sede.last()
    #     else:
    #         return cls.objects.none()
    #
    #     titoli = volunteer.titoli_personali_confermati().filter(
    #                                             titolo__tipo=Titolo.TITOLO_CRI)
    #     courses_list = list()
    #     courses = cls.pubblici().filter(tipo=Corso.CORSO_NUOVO)
    #     for course in courses:
    #         # Course has extensions.
    #         # Filter courses by titles and sede comparsion
    #         if course.has_extensions():
    #             volunteer_titolo = titoli.values_list('titolo', flat=True)
    #             t = course.get_extensions_titles()
    #             s = course.get_extensions_sede()
    #             ext_t_list = t.values_list('id', flat=True)
    #
    #             # Course has required titles but volunteer has not at least one
    #             if t and not volunteer.has_required_titles_for_course(course):
    #                 continue
    #
    #             if s and (sede in s):
    #                 courses_list.append(course.pk)
    #             else:
    #                 # Extensions have sede but volunteer's sede is not in the list
    #                 continue
    #         else:
    #             # Course has no extensions.
    #             # Filter by firmatario sede if sede of volunteer is the same
    #             firmatario = course.get_firmatario_sede
    #             if firmatario and (sede in [firmatario]):
    #                 courses_list.append(course.pk)
    #
    #     return CorsoBase.objects.filter(id__in=courses_list)

    @property
    def iniziato(self):
        return self.data_inizio < timezone.now()

    @property
    def prevede_evento(self):
        return self.evento

    @property
    def troppo_tardi_per_iscriverti(self):
        return  timezone.now() > (self.data_inizio + datetime.timedelta(days=settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI))

    @property
    def possibile_aggiungere_iscritti(self):
        return self.stato in [Corso.ATTIVO, Corso.PREPARAZIONE]

    @property
    def possibile_cancellare_iscritti(self):
        return self.stato in [Corso.ATTIVO, Corso.PREPARAZIONE]

    @property
    def url(self):
        return "/aspirante/corso-base/%d/" % self.pk

    @property
    def sigla_corso(self):
        titolo_cri = self.titolo_cri
        sigla_titolo = '%s/' % titolo_cri.sigla if hasattr(titolo_cri, 'sigla') and titolo_cri.sigla else ''
        return "%s/%s/%s%s" % (self.sede.sede_regionale_sigla, self.anno, sigla_titolo, self.progressivo)

    @property
    def nome(self):
        course_type = 'Corso Base' if self.tipo == Corso.BASE else 'Corso'
        titolo_cri = self.titolo_cri if self.titolo_cri else course_type

        return "%s %s" % (titolo_cri, self.sigla_corso)

    @property
    def link(self):
        return '<a href="%s">%s</a>' % (self.url, self.nome)

    @property
    def url_direttori(self):
        return "/formazione/corsi-base/%d/direttori/" % (self.pk,)

    @property
    def url_annulla(self):
        return reverse('aspirante:annulla', args=[self.pk])

    @property
    def url_commissione_esame(self):
        return reverse('courses:commissione_esame', args=[self.pk])

    @property
    def url_modifica(self):
        return reverse('aspirante:modify', args=[self.pk])

    @property
    def url_attiva(self):
        return reverse('aspirante:activate', args=[self.pk])

    @property
    def url_termina(self):
        return reverse('aspirante:terminate', args=[self.pk])

    @property
    def url_iscritti(self):
        return "%siscritti/" % (self.url,)

    @property
    def url_iscritti_aggiungi(self):
        return "%siscritti/aggiungi/" % (self.url,)

    @property
    def url_iscriviti(self):
        return "%siscriviti/" % (self.url,)

    @property
    def url_ritirati(self):
        return "%sritirati/" % (self.url,)

    @property
    def url_mappa(self):
        return reverse('aspirante:map', args=[self.pk])

    @property
    def url_lezioni(self):
        return reverse('aspirante:lessons', args=[self.pk])

    @property
    def url_report(self):
        return reverse('aspirante:report', args=[self.pk])

    @property
    def url_firme(self):
        return reverse('aspirante:firme', args=[self.pk])

    @property
    def url_report_schede(self):
        return reverse('aspirante:report_schede', args=[self.pk])

    @property
    def url_estensioni(self):
        return reverse('aspirante:estensioni_modifica', args=[self.pk])

    @classmethod
    def nuovo(cls, anno=None, **kwargs):
        """
        Metodo per creare un nuovo corso. Crea progressivo automaticamente.
        :param anno: Anno di creazione del corso.
        :param kwargs: Parametri per la creazione del corso.
        :return:
        """

        anno = anno or datetime.date.today().year
        try:  # Per il progressivo, cerca ultimo corso
            ultimo = cls.objects.filter(anno=anno).latest('progressivo')
            progressivo = ultimo.progressivo + 1
        except:
            progressivo = 1  # Se non esiste, inizia da 1

        c = CorsoBase(anno=anno, progressivo=progressivo, **kwargs)
        c.min_participants, c.max_participants = c.titolo_cri.numero_partecipazioni
        c.save()
        return c

    @property
    def has_scheda_lezioni(self):
        return True if self.titolo_cri and self.titolo_cri.scheda_lezioni else False

    def get_lezioni_precaricate(self):
        if self.has_scheda_lezioni:
            return LezioneCorsoBase.objects.filter(corso=self,
                                                   scheda_lezione_num__isnull=False)
        return LezioneCorsoBase.objects.none()

    def create_lezioni_precaricate(self):
        if self.has_scheda_lezioni:
            scheda = self.titolo_cri.scheda_lezioni
            lezioni_nums = scheda.keys()

            existing = LezioneCorsoBase.objects.filter(
                corso=self, scheda_lezione_num__in=list(lezioni_nums)
            ).values_list('scheda_lezione_num', flat=True)
            existing = list(map(str, existing))

            lezioni_nums_to_create = set(existing) ^ set(lezioni_nums)

            lezioni_corso = [
                LezioneCorsoBase(
                    corso=self,
                    inizio=self.data_inizio.replace(hour=0, minute=0, second=0),
                    nome=lezione['lezione'],
                    scheda_lezione_num=lezione_num,
                ) for lezione_num, lezione in self.titolo_cri.scheda_lezioni.items()
                if lezione_num in lezioni_nums_to_create
            ]
            lezioni_created = LezioneCorsoBase.objects.bulk_create(lezioni_corso)
            return lezioni_created
        else:
            print('Il corso non ha <scheda_lezioni>')

    def get_or_create_lezioni_precompilate(self):
        if self.has_scheda_lezioni:
            if len(self.titolo_cri.scheda_lezioni.keys()) != len(self.get_lezioni_precaricate()):
                return self.create_lezioni_precaricate()
        return self.get_lezioni_precaricate()

    def get_lezione_sicurezza_salute_volontario(self):
        for lezione in self.get_lezioni_precaricate():
            if lezione.is_lezione_salute_e_sicurezza:
                return lezione
        return LezioneCorsoBase.objects.none()

    @property
    def ha_lezioni_non_revisionate(self):
        lezioni = self.get_lezioni_precaricate()
        if lezioni:
            return True in [lezione.non_revisionata for lezione in lezioni]
        return False

    def attivabile(self):
        """Controlla se il corso base e' attivabile."""

        if not self.locazione and self.tipo not in [Corso.CORSO_ONLINE, Corso.BASE_ONLINE]:
            return False

        if not self.descrizione:
            return False

        # if self.is_nuovo_corso and self.extension_type !=
        #     CorsoBase.EXT_LVL_REGIONALE:
        #     return False

        # if self.has_scheda_lezioni and self.ha_lezioni_non_revisionate:
        #     return False

        if self.direttori_corso().count() == 0:
            return False

        return True

    def aspiranti_nelle_vicinanze(self):
        from formazione.models import Aspirante
        if self.locazione:
            aspiranti = self.circonferenze_contenenti(Aspirante.query_contattabili())
            logger.info("Aspiranti nelle vicinanze: {}".format(aspiranti))
            return aspiranti
        else:
            aspiranti = self.sede.circonferenze_contenenti(Aspirante.query_contattabili())
            logger.info("Aspiranti nelle vicinanze: {}".format(aspiranti))
            return aspiranti

    def partecipazioni_confermate_o_in_attesa(self):
        return self.partecipazioni_confermate() | self.partecipazioni_in_attesa()

    def partecipazioni_confermate(self):
        return PartecipazioneCorsoBase.con_esito_ok(corso=self)

    def partecipazioni_confermate_assente_motivo(self, solo=False):
        """ solo:
        False (default):
            - Restituisce partecipazioni confermate SENZA motivo assente
        True:
            - Restituisce SOLO partecipazioni confermate CON assenti per motivo giustificato.
        """

        condition = {'esaminato_seconda_data': True}
        if solo:
            return self.partecipazioni_confermate().filter(**condition)
        else:
            return self.partecipazioni_confermate().exclude(**condition)

    def partecipazioni_confermate_prova_pratica(self):
        return self.partecipazioni_confermate().filter(partecipazione_online_da_sostenere=True)


    @property
    def terminabile_con_assenti_motivazione(self):
        ha_assenti = self.has_partecipazioni_confermate_con_assente_motivo
        if self.relazione_direttore.is_completed:
            if ha_assenti and self.data_esame_2 > timezone.now() >= self.data_esame:
                return True
            if not ha_assenti and timezone.now() > self.data_esame_2:
                return True
        return False

    @property
    def has_partecipazioni_confermate_esame_seconda_data(self):
        return self.partecipazioni_confermate().filter(
            esaminato_seconda_data=True).exists()

    @property
    def has_partecipazioni_confermate_prova_pratica(self):
        return self.partecipazioni_confermate().filter(partecipazione_online_da_sostenere=True).exists()

    @property
    def has_partecipazioni_confermate_con_assente_motivo(self):
        return self.partecipazioni_confermate().filter(
            ammissione=PartecipazioneCorsoBase.ASSENTE_MOTIVO).exists()

    @property
    def commissione_nomi_as_list(self):
        if self.commissione_esame_names:
            return [i.strip() for i in self.commissione_esame_names.split(',')]
        return list()

    @property
    def ha_compilato_commissione_esame(self):
        if self.titolo_cri and not self.titolo_cri.scheda_prevede_esame:
            return True  # Considera compilato se corso non prevede esame

        if self.commissione_esame_file and self.commissione_esame_names:
            return True
        return False

    @property
    def esame_previsto(self):
        if self.corso_vecchio:
            return True

        if self.titolo_cri:
            if not self.titolo_cri.scheda_prevede_esame:
                return False
            if self.titolo_cri.scheda_esame_facoltativo == True:
                return False
        return True

    def partecipazioni_in_attesa(self):
        return PartecipazioneCorsoBase.con_esito_pending(corso=self)

    def inviti_confermati_o_in_attesa(self):
        return self.inviti_confermati() | self.inviti_in_attesa()

    def inviti_confermati(self):
        return InvitoCorsoBase.con_esito_ok(corso=self)

    def inviti_in_attesa(self):
        return InvitoCorsoBase.con_esito_pending(corso=self)

    def numero_partecipazioni_in_attesa_e_inviti(self):
        return self.partecipazioni_in_attesa().count() + self.inviti_in_attesa().count()

    def partecipazioni_negate(self):
        return PartecipazioneCorsoBase.con_esito_no(corso=self)

    def partecipazioni_ritirate(self):
        return PartecipazioneCorsoBase.con_esito_ritirata(corso=self)

    def attiva(self, request=None, rispondi_a=None):
        from .tasks import task_invia_email_agli_aspiranti

        if not self.attivabile():
            raise ValueError("Questo corso non è attivabile.")

        if self.is_nuovo_corso or self.online:
            messaggio = "A breve tutti i volontari dei segmenti selezionati "\
                        "verranno informati dell'attivazione di questo corso."
        else:
            messaggio = "A breve tutti gli aspiranti nelle vicinanze verranno "\
                        "informati dell'attivazione di questo corso base."

        self.data_attivazione = now()
        self.stato = self.ATTIVO
        self.save()
        if not self.evento:
            task_invia_email_agli_aspiranti.apply_async(args=(self.pk, rispondi_a.pk),)
        else:
            self.mail_attivazione_corso_per_responsabili_evento()

        self.mail_attivazione_con_delibera()

        return messaggio_generico(request, rispondi_a,
            titolo="Corso attivato con successo",
            messaggio=messaggio,
            torna_titolo="Torna al Corso",
            torna_url=self.url)

    def annulla(self, persona):
        if not self.annullabile:
            raise ValueError("Questo corso non è annullabile.")

        self.stato = self.ANNULLATO

        self.save()

        for partecipazione in self.partecipazioni_confermate_o_in_attesa():
            partecipazione.annulla(persona)
            if (self.online and self.moodle) or self.tipo == Corso.BASE_ONLINE:
                api = TrainingApi()
                api.cancellazione_iscritto(persona=partecipazione.persona, corso=self)

        direttori_deleghe = self.direttori_corso(as_delega=True)
        for direttore in direttori_deleghe:
            p = direttore.persona
            direttore.termina(mittente=persona)
            Messaggio.costruisci_e_accoda(
                oggetto="Annullamento corso: {}".format(self),
                modello='email_corso_annullamanto_direttore.html',
                corpo={
                    'nome': p.nome_completo,
                    "persona": persona.nome_completo,
                    "corso": self
                },
                destinatari=[p, ]
            )

        docenti = self.docenti_corso()
        for docente in docenti:
            Messaggio.costruisci_e_accoda(
                oggetto="Annullamento corso: {}".format(self),
                modello='email_corso_annullamanto_docenti.html',
                corpo={
                    'nome': docente.nome_completo,
                    "persona": persona.nome_completo,
                    "corso": self
                },
                destinatari=[docente, ]
            )

        self.notifica_annullamento_corso()

    def _corso_activation_recipients_for_email(self):
        """
        Trovare destinatari aspiranti o volontari da avvisare di un nuovo corso attivato.
        :return: <Persona>QuerySet
        """

        if self.titolo_cri and self.titolo_cri.is_titolo_corso_base:
            aspiranti_list = self.aspiranti_nelle_vicinanze().values_list('persona', flat=True)
            persone = Persona.objects.filter(pk__in=aspiranti_list)
            logger.info('aspitanti persone: {}'.format(persone))
        else:
            persone = self.get_volunteers_by_course_requirements()
            logger.info('volontari persone: {}'.format(persone))
        return persone

    def _corso_activation_recipients_for_email_generator(self):
        """
        :return: generator
        """
        from django.core.paginator import Paginator

        splitted = Paginator(self._corso_activation_recipients_for_email(), FORMAZIONE_MASSMAIL_CHUNK)
        logger.info('page : {}'.format(splitted.page_range))
        for i in splitted.page_range:
            current_page = splitted.page(i)
            current_qs = current_page.object_list
            logger.info('object_list : {}'.format(current_qs))
            yield current_qs

    def _invia_email_agli_aspiranti(self, rispondi_a=None):

        if self.is_nuovo_corso:
            logger.info('Corso per volontari')
            subject = "Nuovo %s per Volontari CRI" % self.titolo_cri
        else:
            logger.info('Corso per aspiranti')
            subject = "Nuovo Corso per Volontari CRI"

        for queryset in self._corso_activation_recipients_for_email_generator():
            logger.info('page persone: {}'.format(queryset))
            for recipient in queryset:

                email_data = dict(
                    oggetto=subject,
                    modello="email_aspirante_corso.html",
                    corpo={
                        'persona': recipient,
                        'corso': self,
                    },
                    destinatari=[recipient],
                    rispondi_a=rispondi_a
                )

                if (self.tipo == Corso.BASE or self.tipo == Corso.BASE_ONLINE) and not recipient.volontario:
                    # Informa solo aspiranti di zona
                    logger.info('accoda mail aspirante: {}'.format(email_data))
                    Messaggio.costruisci_e_accoda(**email_data)
                    logger.info('accoda mail: {}'.format(email_data))

                if self.is_nuovo_corso:
                    # Informa volontari secondo le estensioni impostate (sedi, segmenti, titoli)
                    Messaggio.costruisci_e_accoda(**email_data)
                    logger.info('accoda mail : {}'.format(email_data))

            time.sleep(FORMAZIONE_MASSMAIL_SLEEP)

    def has_extensions(self, is_active=True, **kwargs):
        """ Case: extension_type == EXT_LVL_REGIONALE """
        return self.corsoestensione_set.filter(is_active=is_active).exists()

    def get_extensions(self, **kwargs):
        """ Returns CorsoEstensione objects related to the course """
        return self.corsoestensione_set.filter(**kwargs)

    def get_extensions_sede(self, with_expanded=True, **kwargs):
        """
        :return: Sede<QuerySet>
        """
        if with_expanded:
            # Restituisce le sedi _CON_ sedi sottostanti
            return self.expand_extensions_sedi_sottostanti()
        else:
            # Restituisce le sedi _SENZA_ sedi sottostanti
            return CorsoEstensione.get_sede(course=self, **kwargs)

    def expand_extensions_sedi_sottostanti(self):
        """
        Restituisce le sedei CON sedi sottostanti di tutte le estensioni del corso.
        :return: Sede<QuerySet>
        """
        expanded = Sede.objects.none()

        for e in self.get_extensions():
            all_sede = e.sede.all()
            expanded |= all_sede
            for sede in all_sede:
                if e.sedi_sottostanti:
                    expanded |= sede.esplora()
        return expanded.distinct()

    def get_extensions_titles(self, **kwargs):
        """ Returns <FormazioneTitle> QuerySet """
        return CorsoEstensione.get_titles(course=self, **kwargs)

    def get_volunteers_by_course_requirements(self, **kwargs):
        """ Da utilizzare solo per i corsi che hanno estensione (nuovi corsi/online) """

        persone_da_informare = None

        corso_extension = self.extension_type

        if CorsoBase.EXT_MIA_SEDE == corso_extension:
            persone_da_informare = self.get_volunteers_by_only_sede()

        if CorsoBase.EXT_LVL_REGIONALE == corso_extension:
            # print(CorsoBase.EXT_LVL_REGIONALE)
            by_ext_sede = self.get_volunteers_by_ext_sede()
            #print('by_ext_sede', by_ext_sede)
            by_ext_titles = self.get_volunteers_by_ext_titles()
            #print('by_ext_titles', by_ext_titles)
            persone_da_informare = by_ext_sede | by_ext_titles

        if persone_da_informare is None:
            persone_da_informare = Persona.objects.none()

        return persone_da_informare.filter(**kwargs).distinct()

    @property
    def get_firmatario(self):
        return self.sede.presidente()

    @property
    def presidente_del_corso(self):
        return self.get_firmatario

    @property
    def get_firmatario_sede(self):
        course_created_by = self.get_firmatario
        if course_created_by is not None:
            return course_created_by.sede_riferimento()
        return course_created_by  # returns None

    def get_volunteers_by_only_sede(self):
        app_attuali = Appartenenza.query_attuale(membro__in=[Appartenenza.VOLONTARIO,
                                                             Appartenenza.DIPENDENTE]).q

        sede = self.sede
        if LOCALE == sede.estensione:
            sede = sede.esplora()
        else:
            sede = [sede]

        app = Appartenenza.objects.filter(app_attuali, sede__in=sede, confermata=True)
        return self._query_get_volunteers_by_sede(app)

    def get_volunteers_by_ext_sede(self):
        segmenti = self.get_segmenti_list()

        app_attuali = Appartenenza.query_attuale(membro__in=segmenti).q
        app = Appartenenza.objects.filter(app_attuali,
                                          sede__in=self.get_extensions_sede(),
                                          confermata=True)
        return self._query_get_volunteers_by_sede(app)

    def _query_get_volunteers_by_sede(self, appartenenze):
        return Persona.to_contact_for_courses(corso=self).filter(
            id__in=appartenenze.values_list('persona__id', flat=True)
        )

    def get_volunteers_by_ext_titles(self):
        sede = self.get_extensions_sede()
        titles = self.get_extensions_titles().values_list('id', flat=True)
        return Persona.objects.filter(sede__in=sede,
                                      titoli_personali__in=titles)

    def get_segmenti_list(self):
        """ Estrarre segmenti dalle estensioni  """
        segmenti = list()
        for estensione in self.get_extensions():
            segmenti.extend(estensione.segmento)
        return segmenti

    @property
    def concluso(self):
        return timezone.now() >= self.data_esame

    @property
    def terminabile(self):
        # Case 1
        case_1 = self.stato == self.ATTIVO \
                 and self.concluso \
                 and self.partecipazioni_confermate().exists()

        if case_1:
            return case_1

        # Case 2 (GAIA-265/Q2)
        lezioni = self.lezioni.all()
        if lezioni:
            ultima_lezione_del_corso = lezioni.order_by('fine').last()
            fine = ultima_lezione_del_corso.fine
            if fine:
                return fine.date() <= now().date()

    @property
    def ha_verbale(self):
        return self.stato == self.TERMINATO and self.partecipazioni_confermate().exists()

    def process_appartenenze(self, partecipante):
        persona = partecipante.persona
        if persona.sostenitore:
            # Termina appartenenza sostenitore quando il corso base è terminato
            app = persona.appartenenze_attuali(membro=Appartenenza.SOSTENITORE)
            for a in app:
                a.fine = now()
                a.terminazione = Appartenenza.DIMISSIONE
                a.save()

    def termina(self, mittente=None, partecipanti_qs=None, **kwargs):
        """ Termina il corso, genera il verbale e
        volontarizza/aggiunge titolo al cv dell'utente """

        data_ottenimento = kwargs.get('data_ottenimento', self.data_esame)
        partecipazioni_idonei_list = list()

        # Per maggiore sicurezza, questa cosa viene eseguita in una transazione
        with transaction.atomic():
            for partecipante in partecipanti_qs:
                if partecipante.ammissione in [PartecipazioneCorsoBase.ASSENTE_MOTIVO,]:
                    # Partecipante con questo motivo non va nel verbale_1
                    continue  # Non fare niente

                if partecipante.ammissione in [PartecipazioneCorsoBase.ESAME_NON_PREVISTO_ASSENTE,]:
                    partecipante.esito_esame = partecipante.NON_IDONEO
                    partecipante.save()
                    continue

                # Calcola e salva l'esito dell'esame
                esito_esame = partecipante.IDONEO if partecipante.idoneo \
                                                else partecipante.NON_IDONEO

                partecipante.esito_esame = esito_esame
                partecipante.save()

                if partecipante.idoneo:
                    partecipazioni_idonei_list.append(partecipante.id)

                # Comunica il risultato all'aspirante/volontario
                partecipante.notifica_esito_esame(mittente=mittente)

                # Actions required only for CorsoBase (Aspirante as participant)
                if not self.is_nuovo_corso:
                    if partecipante.idoneo:  # Se idoneo, volontarizza
                        partecipante.persona.da_aspirante_a_volontario(
                            inizio=self.data_esame,
                            sede=partecipante.destinazione,
                            mittente=mittente
                        )

            # Cancella tutte le eventuali partecipazioni in attesa
            PartecipazioneCorsoBase.con_esito_pending(corso=self).delete()

            # Cambia stato solo se i verbali sono stati completati correttamente
            if not self.has_partecipazioni_confermate_con_assente_motivo:
                # Salva lo stato del corso come terminato
                self.stato = Corso.TERMINATO

                self.process_appartenenze(partecipante)

            self.save()

        if self.stato == Corso.TERMINATO:
            partecipanti_a_chi_dare_titolo_cri = partecipanti_qs.filter(id__in=partecipazioni_idonei_list)
            self.set_titolo_cri_to_participants(partecipanti_a_chi_dare_titolo_cri,
                                                data_ottenimento=data_ottenimento)

    def set_titolo_cri_to_participants(self, partecipanti, **kwargs):
        """ Sets <titolo_cri> in Persona's Curriculum (TitoloPersonale) """

        from curriculum.models import TitoloPersonale

        # if self.corso_vecchio:
        #     data_scadenza = None
        # else:
        #     data_scadenza = timezone.now() + self.titolo_cri.expires_after_timedelta

        objs = [
            TitoloPersonale(
                confermata=True,
                titolo=self.titolo_cri,
                persona=p.persona,
                certificato_da=self.get_firmatario,
                data_ottenimento=kwargs.get('data_ottenimento'),
                data_scadenza=None,  # OBS: GAIA-184
                is_course_title=True,
                corso_partecipazione=p
            )
            for p in partecipanti
        ]
        TitoloPersonale.objects.bulk_create(objs)

    def non_idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.NON_IDONEO)

    def idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.IDONEO)

    def genera_pdf_firme(self, request=None):
        """ Genera il fogli firme delle lezioni del corso. """

        def key_cognome(elem):
           return elem.cognome

        def lezione_suffix(lezione_datetime):
            try:
                return str(lezione_datetime.time()).split('.')[0].replace(':', '-')
            except:
                return ''

        iscritti = [partecipazione.persona for partecipazione in self.partecipazioni_confermate()]

        archivio = Zip(oggetto=self)
        for lezione in self.lezioni.all():
            lezione_inizio, lezione_fine = lezione_suffix(lezione.inizio), lezione_suffix(lezione.fine)
            pdf = PDF(oggetto=self)
            pdf.genera_e_salva_con_python(
                nome="Firme lezione %s (%s - %s).pdf" % (lezione.nome, lezione_inizio, lezione_fine),
                corpo={
                    "corso": self,
                    "iscritti": sorted(iscritti, key=key_cognome),
                    "lezione": lezione,
                    "data": lezione.inizio,
                    'request': request,
                },
                modello="pdf_firme_lezione.html",
            )
            archivio.aggiungi_file(file_path=pdf.file.path, nome_file=pdf.nome)

        archivio.comprimi_e_salva(nome="Fogli firme %s.zip" % self.nome)

        return archivio

    def genera_pdf(self, request=None, **kwargs):
        """
        Genera il verbale del corso.
        """

        anteprima = True if 'anteprima' in request.GET else False

        def key_cognome(elem):
            return elem.persona.cognome

        if not self.ha_verbale:
            if not anteprima:
                raise ValueError("Questo corso non ha un verbale.")

        verbale_per_seconda_data_esame = True if 'seconda_data_esame' in request.GET else False

        partecipazioni = self.partecipazioni_confermate_assente_motivo(solo=verbale_per_seconda_data_esame)

        pdf_template = "pdf_corso_%sesame_verbale.html"
        pdf_template = pdf_template % 'base_' if self.corso_vecchio else pdf_template % ''

        numero_assenti_no_esame = self.partecipazioni_confermate().filter(
            ammissione=PartecipazioneCorsoBase.ESAME_NON_PREVISTO_ASSENTE)

        if verbale_per_seconda_data_esame:
            numero_aspiranti = self.partecipazioni_confermate().filter(esaminato_seconda_data=True)
        else:
            numero_aspiranti = self.partecipazioni_confermate().filter(
                esaminato_seconda_data=False
            ).exclude(
                ammissione__in=[PartecipazioneCorsoBase.ASSENTE, PartecipazioneCorsoBase.ASSENTE_MOTIVO],
            )

        numero_idonei = len([p.pk for p in numero_aspiranti if p.idoneo])
        numero_non_idonei = len([p.pk for p in numero_aspiranti if not p.idoneo])

        pdf = PDF(oggetto=self)
        pdf.genera_e_salva_con_python(
            nome="Verbale Esame del Corso Base %d-%d.pdf" % (self.progressivo, self.anno),
            corpo={
                "corso": self,
                'titolo': "Anteprima " if anteprima else "",
                'secondo_verbale': verbale_per_seconda_data_esame,
                "partecipazioni": sorted(partecipazioni, key=key_cognome),
                "numero_idonei": numero_idonei,
                "numero_non_idonei": numero_non_idonei,
                "numero_aspiranti": numero_aspiranti.count(),
                'numero_assenti_no_esame': numero_assenti_no_esame,
                'request': request,
            },
            modello=pdf_template,
        )

        return pdf

    @property
    def is_reached_max_participants_limit(self):
        confirmed_requests = self.partecipazioni_confermate().count()
        return self.max_participants + 10 == confirmed_requests

    def avvisa_presidente_raggiunto_limite_partecipazioni(self):
        query_kwargs = {
            'oggetto': "Raggiunto limite di partecipazioni %s" % self.nome,
        }

        today = timezone.now().today()
        has_already_sent = Messaggio.objects.filter(
            oggetti_destinatario__persona__in=[self.presidente_del_corso],
            creazione__year=today.year,
            creazione__month=today.month,
            creazione__day=today.day,
            **query_kwargs).exists()

        if not has_already_sent:
            Messaggio.costruisci_e_invia(
                destinatari=[self.presidente_del_corso],
                modello="email_corso_raggiunto_limite_partecipazioni.html",
                corpo={"corso": self}, **query_kwargs)

    @property
    def is_nuovo_corso(self):
        return self.tipo == Corso.CORSO_NUOVO or self.tipo == Corso.CORSO_ONLINE or self.tipo == Corso.CORSO_EQUIPOLLENZA

    def get_course_links(self):
        return self.corsolink_set.filter(is_enabled=True)

    def get_course_files(self):
        return self.corsofile_set.filter(is_enabled=True)

    @property
    def livello(self):
        if self.titolo_cri:
            return self.titolo_cri.cdf_livello

    def inform_presidency_with_delibera_file(self):
        sede = self.sede.estensione
        oggetto = "Delibera nuovo corso: %s" % self
        email_destinatari = ['formazione@cri.it',]

        if self.livello in [Titolo.CDF_LIVELLO_I, Titolo.CDF_LIVELLO_II]:
            # Se indicato, l'indirizzo invia una copia sulla mail della sede regionale
            sede_regionale = self.sede.sede_regionale
            sede_regionale_email = sede_regionale.email if hasattr(sede_regionale, 'email') else None
            if sede_regionale_email:
                email_destinatari.append(sede_regionale_email)

        elif self.livello in [Titolo.CDF_LIVELLO_III, Titolo.CDF_LIVELLO_IV]:
            pass

        if sede == REGIONALE:
            # Invia e-mail
            Messaggio.invia_raw(
                oggetto=oggetto,
                corpo_html="""<p>E' stato attivato un nuovo corso. La delibera si trova in allegato.</p>""",
                email_mittente=Messaggio.NOREPLY_EMAIL,
                lista_email_destinatari=email_destinatari,
                allegati=self.delibera_file
            )

    def mail_attivazione_corso_per_responsabili_evento(self):
        Messaggio.costruisci_e_accoda(
            oggetto="Attivazione Corso: %s" % self,
            modello='email_attivazione_corso_responsabile_evento.html',
            corpo={
                'direttore': self.direttori_corso().first(),
                'corso': self
            },
            destinatari=[delega.persona for delega in self.evento.deleghe_attuali(tipo=RESPONSABILE_EVENTO)],
        )

    # GAIA 306
    def mail_attivazione_con_delibera(self):
        sede = self.sede.estensione
        oggetto = "Delibera nuovo corso: %s" % self

        if not sede == NAZIONALE:
            sede = self.sede.sede_regionale
            sede_regionale = sede if not sede.pk == 1638 else Sede.objects.get(pk=524)
            email_to = sede_regionale.presidente()

            corpo = {
                "corso": self,
                "direttore": self.direttori_corso().first()
            }

            # Invia posta
            Messaggio.costruisci_e_accoda(
                oggetto=oggetto,
                modello='email_attivazione_corso_presidente_regionale.html',
                corpo=corpo,
                destinatari=[email_to,],
                allegati=[self.delibera_file,]
            )

            delegato_fomazione = sede_regionale.delegati_formazione()
            if delegato_fomazione:
                # Invia e-mail delegato_fomazione
                Messaggio.invia_raw(
                    oggetto=oggetto,
                    corpo_html=get_template('email_attivazione_corso_responsabile_fomazione_regionale.html').render(corpo),
                    email_mittente=Messaggio.NOREPLY_EMAIL,
                    lista_email_destinatari=[delegato.email for delegato in delegato_fomazione],
                    allegati=self.delibera_file
                )

                # Invia posta delegato_fomazione
                Messaggio.costruisci_e_accoda(
                    oggetto=oggetto,
                    modello='email_attivazione_corso_responsabile_fomazione_regionale.html',
                    corpo=corpo,
                    destinatari=delegato_fomazione,
                    allegati=[self.delibera_file, ]
                )

    def notifica_annullamento_corso(self):
        sede = self.sede.estensione
        oggetto = "Annullamento corso: %s" % self

        email_destinatari = ['formazione@cri.it', ]

        if self.livello in [Titolo.CDF_LIVELLO_I, Titolo.CDF_LIVELLO_II]:
            # Se indicato, l'indirizzo invia una copia sulla mail della sede regionale
            sede_regionale = self.sede.sede_regionale
            sede_regionale_email = sede_regionale.email if hasattr(sede_regionale, 'email') else None
            if sede_regionale_email:
                email_destinatari.append(sede_regionale_email)

        elif self.livello in [Titolo.CDF_LIVELLO_III, Titolo.CDF_LIVELLO_IV]:
            pass

        if sede == REGIONALE:
            # Invia e-mail
            Messaggio.invia_raw(
                oggetto=oggetto,
                corpo_html=get_template('email_corso_annullamento_al_presidente_responsavile_formazione.html').render(
                    {
                        'corso': self
                    }
                ),
                email_mittente=Messaggio.NOREPLY_EMAIL,
                lista_email_destinatari=email_destinatari
            )

        if not sede == NAZIONALE:
            sede_regionale = self.sede.sede_regionale

            email_to = sede_regionale.presidente()
            # Invia posta
            Messaggio.costruisci_e_accoda(
                oggetto=oggetto,
                modello='email_corso_annullamento_al_presidente_responsavile_formazione.html',
                corpo={
                    'corso': self,
                },
                destinatari=[email_to,]
            )

            delegato_fomazione = sede_regionale.delegati_formazione()

            # Invia e-mail delegato_fomazione
            for delegato in delegato_fomazione:
                Messaggio.invia_raw(
                    oggetto=oggetto,
                    corpo_html=get_template('email_corso_annullamento_al_presidente_responsavile_formazione.html').render(
                        {
                            'corso': self
                        }
                    ),
                    email_mittente=Messaggio.NOREPLY_EMAIL,
                    lista_email_destinatari=[delegato.email]
                )

                # Invia posta delegato_fomazione
                Messaggio.costruisci_e_accoda(
                    oggetto=oggetto,
                    modello='email_corso_annullamento_al_presidente_responsavile_formazione.html',
                    corpo={
                        'corso': self
                    },
                    destinatari=[delegato, ]
                )




    @property
    def presidente_corso(self):
        """Restituisce <Persona> che aveva la delega di PRESIDENTE al giorno dell'esame."""
        return self.sede.delegati_attuali(tipo=PRESIDENTE,
                                          al_giorno=self.data_esame,
                                          solo_deleghe_attive=False).last()

    def direttori_corso(self, as_delega=False):
        """
        :param as_delega (True): return Delega<QuerySet>
        :param as_delega (False): return Persona<QuerySet>
        """
        oggetto_tipo = ContentType.objects.get_for_model(self)
        deleghe = Delega.objects.filter(tipo=DIRETTORE_CORSO,
                                        oggetto_tipo=oggetto_tipo.pk,
                                        oggetto_id=self.pk)
        if as_delega == True:
            return deleghe

        deleghe_persone_id = deleghe.values_list('persona__id', flat=True)
        persone_qs = Persona.objects.filter(id__in=deleghe_persone_id)
        return persone_qs

    def docenti_corso(self):
        docenti_ids = self.lezioni.all().values_list('docente', flat=True)
        return Persona.objects.filter(id__in=docenti_ids)

    def docenti_esterni_corso(self):
        docenti_esterni = self.lezioni.all().values_list('docente_esterno',  flat=True)
        docenti_esterni_result = list()

        HIGHLIGHT_NAME_SYMBOL = '"'

        if not docenti_esterni:
            return docenti_esterni_result

        try:

            join_docenti_esterni = ''.join(list(map(lambda x: '' if not x else x, docenti_esterni)))

            if HIGHLIGHT_NAME_SYMBOL in join_docenti_esterni:
                pattern = r'.*?\%s(.*)%s.*' % (HIGHLIGHT_NAME_SYMBOL, HIGHLIGHT_NAME_SYMBOL)
                for docente in docenti_esterni:
                    match = re.search(pattern, docente)
                    if match is not None:
                        name = match.group(1).strip()
                        if name not in docenti_esterni_result:
                            docenti_esterni_result.append(name.strip())
            elif "/" in join_docenti_esterni:
                for i in docenti_esterni:
                    names = i.split('/')
                    docenti_esterni_result.extend(list(map(lambda x: x.strip(), names)))
            else:
                docenti_esterni_result = docenti_esterni

            # rimuovi valori vuoti, doppioni
            return list(set(filter(bool, docenti_esterni_result)))

        except:
            # per qualsiasi problema, per evitare 500.
            return list()

    def can_modify(self, me):
        if me and me.permessi_almeno(self, MODIFICA):
            return True
        return False

    def can_activate(self, me):
        if me.is_presidente or (me.is_presidente and me in self.direttori_corso()):
            has_delibera = self.delibera_file is not None  # ha caricato delibera
            # has_extension = self.has_extensions()
            has_directors = self.direttori_corso().count() > 0  # ha nominato almeno un direttore
            is_all_true = has_delibera, has_directors  # has_extension,

            # Deve riapparire se: il direttore ha inserito la descrizione
            # if self.descrizione:
            #     return True

            if False in is_all_true:
                return False
            return True
        else:
            """ Direttori del corso vedono sempre la sezione invece """
            return True

    @property
    def relazione_direttore(self):
        # Non creare record in db per un corso ancora in preparazione
        if self.stato != CorsoBase.PREPARAZIONE:
            relazione, created = RelazioneCorso.objects.get_or_create(corso=self)
            return relazione

        return RelazioneCorso.objects.none()

    @property
    def corso_vecchio(self):
        """ Verifica se il corso appartiene al "vecchio" modulo formazione (
        prima dell'aggiornamento del 31/08/2019) """

        if not self.titolo_cri:
            return True
        elif self.titolo_cri:
            return False
        # elif self.creazione < timezone.datetime(2019, 9, 1):
        #     return True
        return False

    @property
    def lezione_salute_sicurezza(self):
        for lezione in self.lezioni.all():
            if lezione.is_lezione_salute_e_sicurezza:
                return lezione
        return None

    @property
    def nominativa_ruoli(self):
        for lezione in self.lezioni.all():
            if lezione.is_nominativa_ruoli:
                return lezione
        return None

    class Meta:
        verbose_name = "Corso"
        verbose_name_plural = "Corsi"
        ordering = ['-anno', '-progressivo']
        permissions = (
            ("view_corsobase", "Can view corso base"),
        )

    def __str__(self):
        return str(self.nome)


class CorsoEstensione(ConMarcaTemporale):
    from multiselectfield import MultiSelectField
    from curriculum.models import Titolo

    corso = models.ForeignKey(CorsoBase, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    segmento = MultiSelectField(max_length=100, choices=Appartenenza.MEMBRO, blank=True)
    titolo = models.ManyToManyField(Titolo, blank=True)
    sede = models.ManyToManyField(Sede)
    sedi_sottostanti = models.BooleanField(default=False, db_index=True,
        help_text='Flaggare "sedi sottostanti" per rendere visibile il corso a tutti '
                  'i Comitati/unità territoriali che afferiscono al Comitato organizzatore; '
                  'qualora non venga messa la spunta, il corso sarà visibile solo alle sedi '
                  'principali e verranno informati solo i Volontari delle stesse'
    )

    # todo: sospeso (GAIA-116/32)
    # PRESIDENTI_COMMISSARI = 'pr'
    # DELEGATI_TECNICI = 'dc'
    # VOLONTARI_GIOVANI = 'vg'
    # VOLONTARI_MAGGIORENNI = 'vm'
    # VOLONTARIO_RUOLI = [
    #     (DELEGATI_TECNICI, "Delegati Tecnici"),
    #     (VOLONTARI_GIOVANI, "Volontari Giovani"),
    #     (VOLONTARI_MAGGIORENNI, "Volontari Maggiorenni"),
    #     (PRESIDENTI_COMMISSARI, "Presidenti / Commissari"),
    # ]
    # segmento_volontario = MultiSelectField(max_length=100, choices=VOLONTARIO_RUOLI, blank=True)

    # AREA_COMITATO = 'a1'
    # AREA_PIU_COMITATI = 'a2'
    # AREA_COMITATO_REGIONALE = 'a3'
    # AREA_LIVELLO_NAZIONALE = 'ac'
    # AREA_GEOGRAFICA_INTERESSATA = [
    #     (AREA_COMITATO, 'Comitato CRI'),
    #     (AREA_PIU_COMITATI, 'Più comitati CRI'),
    #     (AREA_COMITATO_REGIONALE, 'Comitato Regionale CRI'),
    #     (AREA_LIVELLO_NAZIONALE, 'A livello nazionale'),
    # ]
    # area_geografica = models.CharField(max_length=3, choices=AREA_GEOGRAFICA_INTERESSATA, blank=True)

    def visible_by_extension_type(self):
        type = self.corso.extension_type
        if type == CorsoBase.EXT_MIA_SEDE:
            self.is_active = False
        elif type == CorsoBase.EXT_LVL_REGIONALE:
            self.is_active = True

    @classmethod
    def get_sede(cls, course, **kwargs):
        sede = cls._get_related_objects_to_course(course, 'sede', **kwargs)
        return sede if sede else Sede.objects.none()

    @classmethod
    def get_titles(cls, course, **kwargs):
        titles = cls._get_related_objects_to_course(course, 'titolo', **kwargs)
        return titles if titles else Titolo.objects.none()

    def get_segmenti(self, sede=None):
        """
        :return: <Appartenenza>QuerySet
        """
        appartenenze = Appartenenza.objects.filter(membro__in=[self.segmento])
        if sede:
            appartenenze = appartenenze.filter(sede=sede)
        return appartenenze.distinct('membro')

    @classmethod
    def _get_related_objects_to_course(cls, course, field, **kwargs):
        course_extensions = cls.objects.filter(corso=course, **kwargs)
        if not course_extensions.exists():
            return None

        objects = []
        for i in course_extensions:
            elem = getattr(i, field).all()
            if elem:
                for e in elem:
                    objects.append(e)
        if objects:
            model = ContentType.objects.get_for_model(objects[0]).model_class()
            return model.objects.filter(id__in=[obj.id for obj in objects]).distinct()

    def __str__(self):
        return '%s' % self.corso if hasattr(self, 'corso') else 'No CorsoBase set.'

    def save(self):
        self.visible_by_extension_type()
        super().save()

    class Meta:
        verbose_name = 'Estensione del Corso'
        verbose_name_plural = 'Estensioni del Corso'


class InvitoCorsoBase(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale, models.Model):
    persona = models.ForeignKey(Persona, related_name='inviti_corsi', on_delete=models.CASCADE)
    corso = models.ForeignKey(CorsoBase, related_name='inviti', on_delete=models.PROTECT)
    invitante = models.ForeignKey(Persona, related_name='+', on_delete=models.CASCADE)

    # Stati per l'iscrizione da parte del direttore
    NON_ISCRITTO = 0
    ISCRITTO = 1
    IN_ATTESA_ASPIRANTE = 2
    INVITO_INVIATO = -1

    RICHIESTA_NOME = "iscrizione a Corso"

    APPROVAZIONE_AUTOMATICA = datetime.timedelta(days=settings.SCADENZA_AUTORIZZAZIONE_AUTOMATICA)

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        with atomic():
            corso = self.corso
            partecipazione = PartecipazioneCorsoBase.objects.create(persona=self.persona, corso=self.corso)
            partecipazione.autorizzazione_concessa()
            if notifiche_attive:
                Messaggio.costruisci_e_invia(
                    oggetto="Iscrizione a Corso Base",
                    modello="email_corso_base_iscritto.html",
                    corpo={
                        "persona": self.persona,
                        "corso": self.corso,
                    },
                    mittente=self.invitante,
                    destinatari=[self.persona]
                )
            self.delete()
            return corso

    def autorizzazione_negata(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        corso = self.corso
        self.delete()
        return corso

    @classmethod
    def cancella_scaduti(cls):
        cls.objects.filter(creazione__lt=now() - datetime.timedelta(days=settings.FORMAZIONE_VALIDITA_INVITI)).delete()

    def richiedi(self, notifiche_attive=True):
        self.autorizzazione_richiedi(
            self.invitante,
            (
                (INCARICO_ASPIRANTE, self.persona)
            ),
            invia_notifiche=self.persona,
            auto=Autorizzazione.NG_AUTO,
            scadenza=self.APPROVAZIONE_AUTOMATICA,
            notifiche_attive=notifiche_attive,
        )

    def annulla(self, mittente=None):
        self.autorizzazioni_ritira()
        Messaggio.costruisci_e_accoda(
            oggetto="Notifica Annullamento corso",
            modello="email_corso_annullamento.html",
            corpo={
                "persona": self.persona,
                "mittente": mittente,
                "corso": self.corso.nome
            },
            mittente=mittente,
            destinatari=[self.persona]
        )

    def disiscrivi(self, mittente=None):
        """
        Disiscrive partecipante dal corso base.
        """
        self.autorizzazioni_ritira()
        Messaggio.costruisci_e_invia(
            oggetto="Annullamento invito al Corso: %s" % self.corso,
            modello="email_aspirante_corso_deiscrizione_invito.html",
            corpo={
                "invito": self,
                "corso": self.corso,
                "persona": self.persona,
                "mittente": mittente,
            },
            mittente=mittente,
            destinatari=[self.persona],
        )
        Messaggio.costruisci_e_invia(
            oggetto="Annullamento invito al Corso: %s" % self.corso,
            modello="email_aspirante_corso_deiscrizione_invito_mittente.html",
            corpo={
                "invito": self,
                "corso": self.corso,
                "persona": self.persona,
                "richiedente": mittente,
            },
            mittente=None,
            destinatari=[mittente],
        )

    class Meta:
        verbose_name = "Invito di partecipazione a corso"
        verbose_name_plural = "Inviti di partecipazione a corso"
        ordering = ('persona__cognome', 'persona__nome', 'persona__codice_fiscale',)
        permissions = (
            ("view_invitocorsobase", "Can view invito partecipazione corso base"),
        )

    def __str__(self):
        return "Invito di part. di <%s> a <%s>" % (self.persona, self.corso)


class PartecipazioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni, ConPDF):
    persona = models.ForeignKey(Persona, related_name='partecipazioni_corsi', on_delete=models.CASCADE)
    corso = models.ForeignKey(CorsoBase, related_name='partecipazioni', on_delete=models.PROTECT)

    # Stati per l'iscrizione da parte del direttore
    NON_ISCRITTO = 0
    ISCRITTO = 1
    IN_ATTESA_ASPIRANTE = 2
    CANCELLATO = 3
    INVITO_INVIATO = -1

    # Dati per la generazione del verbale (esito)
    POSITIVO = "P"
    NEGATIVO = "N"
    NON_PREVISTO = "O"
    ESITO = (
        (POSITIVO, "Positivo"),
        (NEGATIVO, "Negativo"),
        (NON_PREVISTO, "Non Previsto"),
    )

    IDONEO = "OK"
    NON_IDONEO = "NO"
    ESITO_IDONEO = (
        (IDONEO, "Idoneo"),
        (NON_IDONEO, "Non Idoneo")
    )
    esito_esame = models.CharField(max_length=2, choices=ESITO_IDONEO, default=None, blank=True, null=True, db_index=True)
    esaminato_seconda_data = models.BooleanField(default=False)

    AMMESSO = "AM"
    NON_AMMESSO = "NA"
    ASSENTE = "AS"
    ASSENTE_MOTIVO = "MO"
    ESAME_NON_PREVISTO = "EN"
    ESAME_NON_PREVISTO_ASSENTE = "PA"
    AMMISSIONE = (
        (AMMESSO, "Ammesso"),
        (NON_AMMESSO, "Non Ammesso"),
        (ASSENTE, "Assente"),
        (ASSENTE_MOTIVO, "Assente per motivo giustificato"),
        (ESAME_NON_PREVISTO, "Esame non previsto"),
        (ESAME_NON_PREVISTO_ASSENTE, "Esame non previsto (partecipante assente)"),
    )

    ammissione = models.CharField(max_length=2, choices=AMMISSIONE, default=None, blank=True, null=True, db_index=True)
    motivo_non_ammissione = models.CharField(max_length=1025, blank=True, null=True)

    # Campi per scheda valutazione del corso base
    esito_parte_1 = models.CharField(max_length=1, choices=ESITO, default=None, blank=True, null=True, db_index=True, help_text="La Croce Rossa.")
    argomento_parte_1 = models.CharField(max_length=1024, blank=True, null=True, help_text="es. Storia della CRI, DIU.")
    esito_parte_2 = models.CharField(max_length=1, choices=ESITO, default=None, blank=True, null=True, db_index=True, help_text="Gesti e manovre salvavita.")
    argomento_parte_2 = models.CharField(max_length=1024, blank=True, null=True, help_text="es. BLS, colpo di calore.")
    partecipazione_online = models.BooleanField(verbose_name="Prova pratica su Parte 2 sostituita da colloquio ONLINE", default=False)

    partecipazione_online_da_sostenere = models.BooleanField(default=False)

    extra_1 = models.BooleanField(verbose_name="Prova pratica su Parte 2 sostituita da colloquio.", default=False)
    extra_2 = models.BooleanField(verbose_name="Verifica effettuata solo sulla Parte 1 del programma del corso.", default=False)
    destinazione = models.ForeignKey("anagrafica.Sede", verbose_name="Sede di destinazione", related_name="aspiranti_destinati", default=None, null=True, blank=True, help_text="La Sede presso la quale verrà registrato come Volontario l'aspirante "
                                               "nel caso di superamento dell'esame.")

    # Campi per scheda valutazione individuale dei corsi nuovi (altri corsi)
    eventuale_tirocinio = models.CharField(_("Eventuale tirocinio/affiancamento"), max_length=1, choices=ESITO, default=None, blank=True, null=True, db_index=True)
    valutazione_complessiva = models.CharField(_("Valutazione complessiva del Direttore del Corso"), max_length=255, null=True, blank=True)
    eventuali_note = models.CharField(_("Eventuali Note/Osservazioni"), max_length=255, null=True, blank=True)

    RICHIESTA_NOME = "Iscrizione Corso"

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        if self.corso.is_nuovo_corso:
            return

        # Quando un aspirante viene iscritto, tutte le richieste presso altri corsi devono essere cancellati
        # Cancella tutte altre partecipazioni con esito pending - ce ne puo' essere solo una.
        PartecipazioneCorsoBase.con_esito_pending(persona=self.persona).exclude(corso=self.corso).delete()

    def ritira(self):
        self.autorizzazioni_ritira()


    def richiedi(self, notifiche_attive=True):
        self.autorizzazione_richiedi(
            self.persona,
                (
                    (INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI, self.corso)
                ),
            invia_notifiche=self.corso.delegati_attuali(),
            notifiche_attive=notifiche_attive
        )

    @property
    def idoneo(self):
        """ Regole per l'idoneità """

        case_1 = (
            self.esito_parte_1 == self.POSITIVO and (
                self.esito_parte_2 == self.POSITIVO or (self.extra_2 and not self.esito_parte_2)
            )
        )

        # --- Per i corsi avviati prima del 01/09/2019 ---
        if self.corso.corso_vecchio:
            return case_1

        # --- Regole per i corsi avviati dopo il 01/09/2019 ---

        # Scheda del corso non prevede esame (e compilare il verbale)
        case_2 = (
            self.ammissione == self.ESAME_NON_PREVISTO and
            self.corso.titolo_cri and not self.corso.titolo_cri.scheda_prevede_esame
        )

        case_3 = (
            self.ammissione == self.AMMESSO and
            self.esito_parte_1 in [self.POSITIVO, self.NON_PREVISTO] and
            self.esito_parte_2 in [self.POSITIVO, self.NON_PREVISTO]

        )

        return case_1 or case_2 or case_3

    def notifica_esito_esame(self, mittente=None):
        """ Invia una e-mail al partecipante con l'esito del proprio esame. """

        template = "email_%s_corso_esito.html"
        if self.corso.is_nuovo_corso:
            template = template % 'volontario'
        else:
            template = template % 'aspirante'

        Messaggio.costruisci_e_invia(
            oggetto="Esito del Corso: %s" % self.corso,
            modello=template,
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
                "mittente": mittente,
            },
            mittente=mittente,
            destinatari=[self.persona],
        )

    def annulla(self, mittente=None):
        self.autorizzazioni_ritira()
        Messaggio.costruisci_e_accoda(
            oggetto="Notifica Annullamento corso",
            modello="email_corso_annullamento.html",
            corpo={
                "persona": self.persona,
                "mittente": mittente,
                "corso": self.corso.nome
            },
            mittente=mittente,
            destinatari=[self.persona]
        )

    def disiscrivi(self, mittente=None):
        """ Disiscrive partecipante dal corso base. """
        self.autorizzazioni_ritira()
        Messaggio.costruisci_e_invia(
            oggetto="Disiscrizione dal Corso: %s" % self.corso,
            modello="email_aspirante_corso_deiscrizione.html",
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
                "mittente": mittente,
            },
            mittente=mittente,
            destinatari=[self.persona],
        )
        Messaggio.costruisci_e_invia(
            oggetto="Disiscrizione dal Corso: %s" % self.corso,
            modello="email_aspirante_corso_deiscrizione_mittente.html",
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
                "richiedente": mittente,
            },
            mittente=None,
            destinatari=[mittente],
        )

    def autorizzazione_concedi_modulo(self):
        from formazione.forms import ModuloConfermaIscrizioneCorso
        return ModuloConfermaIscrizioneCorso  # GAIA-124

        # if self.corso.is_nuovo_corso:
        #     return ModuloConfermaIscrizioneCorso
        # else:
        #     return ModuloConfermaIscrizioneCorsoBase

    @classmethod
    def partecipazioni_ordinate_per_attestato(cls, corso):
        from collections import OrderedDict

        partecipanti_con_attestato = corso.partecipazioni_confermate().order_by('persona__cognome')
        return OrderedDict(
            [(i.persona.pk, line) for line, i in enumerate(partecipanti_con_attestato, 1)]
        )

    def get_partecipazione_id_per_attestato(self, corso, persona_pk):
        return self.partecipazioni_ordinate_per_attestato(corso).get(persona_pk)

    def genera_scheda_valutazione(self, request=None):
        pdf = PDF(oggetto=self)

        # Decidi sul template sulla base del tipo e della versione del modulo <formazione>
        pdf_template = "pdf_corso_%sscheda_valutazione.html"
        if self.corso.corso_vecchio:
            pdf_template = pdf_template % "base_"
        else:
            if self.corso.is_nuovo_corso:
                pdf_template = pdf_template % ""
            else:
                pdf_template = "pdf_corso_base_scheda_valutazione_nuova.html"

        pdf.genera_e_salva_con_python(
            nome="Scheda Valutazione %s.pdf" % self.persona.codice_fiscale,
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
                'request': request,
            },
            modello=pdf_template,
        )
        return pdf

    def genera_attestato(self, request=None):
        if not self.idoneo:
            return None

        pdf_template = "pdf_corso_attestato.html"

        # Usare il vecchio attestato per i corsi senza titolo (creati prima del 01/09/2019)
        if not self.corso.titolo_cri:
            pdf_template = "pdf_corso_base_attestato.html"

        corso, persona = self.corso, self.persona

        pdf = PDF(oggetto=self)
        pdf.genera_e_salva_con_python(
            nome="Attestato %s.pdf" % self.persona.codice_fiscale,
            corpo={
                "partecipazione": self,
                "corso": corso,
                "persona": persona,
                "request": request,
                'partecipazione_id':
                    self.get_partecipazione_id_per_attestato(corso, persona.pk)
            },
            modello=pdf_template,
        )
        return pdf

    def genera_pdf(self, request=None, **kwargs):
        scheda_valutazione = self.genera_scheda_valutazione(request)
        attestato = self.genera_attestato(request)

        z = Zip(oggetto=self)
        z.aggiungi_file(scheda_valutazione.file.path)

        if self.idoneo:
            z.aggiungi_file(attestato.file.path)

        z.comprimi_e_salva("%s.zip" % self.persona.codice_fiscale)

        return z

    @classmethod
    def controlla_richiesta_processabile(cls, richiesta):
        # Caso: autorizzazzione non è del tipo del Corso
        tipo = ContentType.objects.get_for_model(cls)
        if richiesta.oggetto_tipo != tipo:
            return True

        # Caso: non è il giorno dell'inizio del Corso (quando si può processare le richieste)
        richiesta_partecipazione = get_object_or_404(cls, pk=richiesta.oggetto_id)
        if richiesta_partecipazione.corso.data_inizio > timezone.now():
            return False
        return True

    @classmethod
    def richieste_non_processabili(cls, richieste):
        tipo = ContentType.objects.get_for_model(cls)
        partecipazioni_da_bloccare = PartecipazioneCorsoBase.objects.filter(
            corso__data_inizio__gt=timezone.now()).values_list('pk', flat=True
                                                               )
        return richieste.filter(
            oggetto_tipo=tipo, oggetto_id__in=partecipazioni_da_bloccare
        ).values_list('pk', flat=True)

    @property
    def assente_lezione_salute_e_sicurezza(self):
        lezione = self.corso.get_lezione_sicurezza_salute_volontario()
        if lezione:
            return AssenzaCorsoBase.objects.filter(
                persona=self.persona,
                lezione=lezione,
            ).exists()
        return False

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"
        ordering = ('persona__cognome', 'persona__nome', 'persona__codice_fiscale',)
        permissions = (
            ("view_partecipazionecorsobarse", "Can view corso Richiesta di partecipazione"),
        )

    def __str__(self):
        return "Richiesta di part. di %s a %s" % (self.persona, self.corso)


class LezioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConStorico):
    corso = models.ForeignKey(CorsoBase, related_name='lezioni', on_delete=models.PROTECT)
    nome = models.TextField()
    docente = models.ManyToManyField(Persona, blank=True, verbose_name='Docente della lezione',)
    docente_esterno = models.CharField('Docente esterno della lezione',
                                       max_length=255, null=True, blank=True,
                                       help_text="Da compilare solo per i docenti esterni")
    obiettivo = models.CharField('Obiettivo formativo della lezione',
                                 max_length=255, null=True, blank=True)
    luogo = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="il luogo di dove si svolgeranno le lezioni",
                             help_text="Compilare nel caso il luogo è diverso "
                                       "dal comitato che ha organizzato il corso.")
    scheda_lezione_num = models.SmallIntegerField(null=True, blank=True)
    lezione_divisa_parent = models.ForeignKey('LezioneCorsoBase', null=True, blank=True)

    @property
    def url_cancella(self):
        return "%s%d/cancella/" % (self.corso.url_lezioni, self.pk)

    @property
    def url_save(self):
        return reverse('courses:lezione_save', args=[self.corso.pk, self.pk])

    def avvisa_docente_nominato_al_corso(self, me):
        docenti = self.docente
        if docenti.count():
            for docente in docenti.all():
                query_kwargs = {
                    'oggetto': 'Docente al %s' % self.corso.nome,
                    'mittente': me,
                }

                # Verifica, per non inviare più volte stessa mail
                msg_already_sent = Messaggio.objects.filter(
                    oggetti_destinatario__persona__in=[docente],
                **query_kwargs).count()

                if not msg_already_sent:
                    Messaggio.costruisci_e_accoda(
                        modello="email_docente_assegnato_a_corso.html",
                        corpo={
                            "persona": docente,
                            "corso": self.corso,
                        }, destinatari=[docente], **query_kwargs)

    def avvisa_presidente_docente_nominato(self):
        """Avvisa presidente del comitato della persona che è stato nominato
        come docente di questa lezione."""

        docenti = self.docente
        if not docenti.count():
            return

        for docente in docenti.all():
            esito = self.corso.sede.ha_membro(docente, membro=Appartenenza.VOLONTARIO)

            if not esito:
                destinatari = list()
                for sede in docente.sedi_attuali(membro__in=[Appartenenza.VOLONTARIO]):

                    destinatari.append(sede.presidente())

                if destinatari:
                    query_kwargs = {
                        'oggetto': "%s è nominato come docente di lezione %s" % (docente, self.nome),
                    }

                    # Verifica, per non inviare più volte stessa mail
                    msg_already_sent = Messaggio.objects.filter(
                        oggetti_destinatario__persona__in=destinatari,
                    **query_kwargs).count()

                    if not msg_already_sent:
                        # GAIA 306
                        # notifica/mail presidente se nominato docente su un altro comitato
                        oggetto = "%s è nominato come docente di lezione %s" % (docente, self.nome)
                        corpo = {
                            "persona": docente,
                            "corso": self.corso,
                            'lezione': self,
                        }
                        # NOTIFICA
                        Messaggio.costruisci_e_accoda(
                            oggetto=oggetto,
                            modello="email_corso_avvisa_presidente_docente_nominato_a_lezione.html",
                            corpo=corpo,
                            destinatari=destinatari,
                        )
                        # MAIL
                        Messaggio.invia_raw(
                            oggetto=oggetto,
                            corpo_html=get_template(
                                "email_corso_avvisa_presidente_docente_nominato_a_lezione.html"
                            ).render(corpo),
                            email_mittente=Messaggio.NOREPLY_EMAIL,
                            lista_email_destinatari=[destinatario.email for destinatario in destinatari]
                        )

    def get_full_scheda_lezioni(self):
        if hasattr(self, 'corso') and self.corso.titolo_cri and self.corso.titolo_cri.scheda_lezioni:
            return self.corso.titolo_cri.scheda_lezioni
        return dict()

    def get_scheda_lezione(self):
        lezione = self.get_full_scheda_lezioni().get(str(self.scheda_lezione_num))
        return lezione if lezione else dict()

    def get_from_scheda(self, key, default=None):
        return self.get_scheda_lezione().get(key, default)

    @property
    def lezione_argomento_splitted(self):
        argomento = self.get_from_scheda('argomento', '')
        return argomento.split('|')

    @property
    def lezione_argomento(self):
        return '; '.join(self.lezione_argomento_splitted)

    @property
    def lezione_ore(self):
        ore = self.get_from_scheda('ore')
        if not ore:
            return ore

        if "’" in ore:
            # Elaborare i valori con apostrofo (minuti)
            minutes = re.findall(r'^\d+', ore.strip())
            minutes = int(minutes[0]) if minutes else 60
            return datetime.timedelta(minutes=minutes)

        elif "," and len(ore) < 5:
            # Valori ore, minuti con virgola (1,5)
            minutes = float(ore.replace(',', '.')) * 60
            return datetime.timedelta(minutes=minutes)

        else:
            try:
                return datetime.timedelta(hours=int(ore))
            except ValueError:
                return datetime.timedelta(hours=1)

    @property
    def lezione_id_univoco(self):
        return self.get_from_scheda('id', "")

    @property
    def precaricata(self):
        if self.scheda_lezione_num:
            return True
        return self.scheda_lezione_num is not None

    @property
    def non_revisionata(self):
        """ La lezione risulta non revisionata se è rimasto il solo valore di
        inizio impostato in automatico con la creazione del corso """
        return self.inizio and not self.fine

    @property
    def divisa(self):
        return True if self.lezione_divisa_parent else False

    @property
    def puo_dividere(self):
        lezioni_divise = LezioneCorsoBase.objects.filter(lezione_divisa_parent=self)
        if not lezioni_divise:
            return True
        elif lezioni_divise.count() < 7:
            return True
        return False

    def dividi(self):
        return LezioneCorsoBase.objects.create(
            corso=self.corso,
            lezione_divisa_parent=self,
            scheda_lezione_num=self.scheda_lezione_num,
            inizio=self.inizio + datetime.timedelta(minutes=60),
            nome=self.nome,
            # docente=self.docente,
            # luogo=self.luogo,
        )

    @property
    def is_lezione_salute_e_sicurezza(self):
        """ GAIA-130: Questa lezione è obbligatoria peri Volontari e senza di essa
        non possono essere ammessi all' esame. """

        if self.precaricata and self.corso.titolo_cri.sigla == 'CRI' and \
                self.lezione_id_univoco.endswith("SESDV"):
            return True
        return False

    @property
    def is_nominativa_ruoli(self):
        """ GAIA-130: Questa lezione è obbligatoria peri Volontari e senza di essa
        non possono essere ammessi all' esame. """

        if self.precaricata and self.corso.titolo_cri.sigla == 'CRIVT' and self.lezione_id_univoco.endswith("6NER"):
            return True
        return False

    class Meta:
        verbose_name = "Lezione di Corso"
        verbose_name_plural = "Lezioni di Corsi"
        ordering = ['scheda_lezione_num', 'inizio',]
        permissions = (
            ("view_lezionecorsobase", "Can view corso Lezione di Corso Base"),
        )

    def __str__(self):
        return "Lezione: %s" % self.nome


class AssenzaCorsoBase(ModelloSemplice, ConMarcaTemporale):
    """
    NB: valorizzati i campi "is_esonero" e "esonero_motivazione" significa
    "Presenza", quindi per ottenere in una queryset solo le persone assenti
    bisogna escludere i risultati con questi 2 campi valorizzati.
    """

    lezione = models.ForeignKey(LezioneCorsoBase, related_name='assenze', on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, related_name='assenze_corsi_base', on_delete=models.CASCADE)
    registrata_da = models.ForeignKey(Persona, related_name='assenze_corsi_base_registrate', null=True, on_delete=models.SET_NULL)

    # Se questi 2 campi hanno un valore, Persona sarà considerata "Presente" alla lezione (GAIA-96)
    esonero = models.NullBooleanField(default=False)
    esonero_motivazione = models.CharField(max_length=255, null=True, blank=True,
                                           verbose_name="Motivazione dell'esonero")

    @classmethod
    def create_assenza(cls, lezione, persona, registrata_da, esonero=None):
        queryset_kwargs = {
            'lezione': lezione,
            'persona': persona,
        }

        try:
            # Trova un assenza con i parametri
            assenza, created = cls.objects.get_or_create(**queryset_kwargs)
        except cls.MultipleObjectsReturned:
            # Trovate più di una assenza, al massimo può esserci una assenza
            # Prendi quella ultima e cancella tutte le altre
            assenza = cls.objects.filter(**queryset_kwargs).last()
            cls.objects.filter(**queryset_kwargs).exclude(id__in=[assenza.id]).delete()

        # Se l'assenza è stata creata da un'altra persona - modificala
        if assenza.registrata_da != registrata_da:
            assenza.registrata_da = registrata_da
            assenza.save()

        if esonero:
            # Scrivi nell'oggetto <Assenza> la motivazione dell'esonero
            assenza.esonero = True
            assenza.esonero_motivazione = esonero
            assenza.save()

        return assenza

    @property
    def is_esonero(self): # , lezione, persona
        if self.esonero and self.esonero_motivazione:
            return True
        if self.esonero or self.esonero_motivazione:
            return True
        return False

    def __str__(self):
        return 'Assenza di %s a %s' % (self.persona.codice_fiscale, self.lezione)

    class Meta:
        verbose_name = "Assenza a Corso"
        verbose_name_plural = "Assenze ai Corsi"
        permissions = (
            ("view_assenzacorsobase", "Can view corso Assenza a Corso Base"),
        )


class Aspirante(ModelloSemplice, ConGeolocalizzazioneRaggio, ConMarcaTemporale):

    persona = models.OneToOneField(Persona, related_name='aspirante')

    # Numero minimo di Comitati nelle vicinanze
    MINIMO_COMITATI = 7

    MINIMO_RAGGIO = 5  # Almeno 4 km.
    MASSIMO_RAGGIO = 50  # Max 40 km.

    RAGGIO_STEP = 1.8

    # Massimo iterazioni nella ricerca
    MASSIMO_ITERAZIONI = (MASSIMO_RAGGIO - MINIMO_RAGGIO) // RAGGIO_STEP

    class Meta:
        verbose_name_plural = "Aspiranti"
        permissions = (
            ("view_aspirante", "Can view corso aspirante"),
        )

    def __str__(self):
        return "Aspirante %s" % (self.persona.nome_completo,)

    def sedi(self, tipo=Sede.COMITATO, **kwargs):
        """
        Ritorna un elenco di Comitati (Sedi) nelle vicinanze dell'Aspirante.
        :param tipo: Il tipo di sede. Default=Sede.COMITATO.
        :return: Un elenco di Sedi.
        """
        return self.nel_raggio(Sede.objects.filter(tipo=tipo, **kwargs))

    def comitati(self):
        return self.sedi().filter(estensione__in=[LOCALE, PROVINCIALE, TERRITORIALE])

    def richiesta_corso(self):
        return CorsoBase.objects.filter(
            PartecipazioneCorsoBase.con_esito_pending(persona=self.persona).via("partecipazioni"),
            stato=Corso.ATTIVO,
        ).first()

    def corsi(self, **kwargs):
        """
        Ritorna un elenco di Corsi (Base) nelle vicinanze dell'Aspirante.
        :return: Un elenco di Corsi.
        """
        corsi = CorsoBase.pubblici().filter(**kwargs)
        return self.nel_raggio(corsi.exclude(tipo=CorsoBase.CORSO_NUOVO))

    def corso(self):
        partecipazione = PartecipazioneCorsoBase.con_esito_ok(persona=self.persona)
        partecipazione = partecipazione.via("partecipazioni")
        corso = CorsoBase.objects.filter(partecipazione, stato=Corso.ATTIVO)
        return corso.first()

    def calcola_raggio(self):
        """
        Calcola il raggio minimo necessario.
        :return: Il nuovo raggio.
        """
        if not self.locazione:
            self.raggio = 0
            self.save()
            return 0

        iterazione = 0
        self.raggio = self.MINIMO_RAGGIO
        while True:
            iterazione += 1
            self.raggio += self.RAGGIO_STEP
            self.save()

            if iterazione >= self.MASSIMO_ITERAZIONI or self.comitati().count() >= self.MINIMO_COMITATI:
                break

        return self.raggio

    def post_locazione(self):
        """
        Ricalcola il raggio automaticamente ogni volta che viene impostata
        una nuova locazione.
        """
        self.calcola_raggio()
        return super(Aspirante, self).post_locazione()

    @classmethod
    @concept
    def query_contattabili(cls, *args, **kwargs):
        """
        Ritorna un queryset di Aspiranti che possono essere contattati
        per l'attivazione di un corso base.

        Ritorna gli aspiranti che non sono iscritti ad alcun corso base.
        :param args:
        :param kwargs:
        :return:
        """
        persone_da_non_contattare = Persona.objects.filter(
            PartecipazioneCorsoBase.con_esito(
                PartecipazioneCorsoBase.ESITO_OK
            ).via("partecipazioni_corsi")
        )

        return Q(
            ~Q(persona__id__in=persone_da_non_contattare.values_list('id', flat=True)),
            *args,
            **kwargs
        )

    @property
    def inviti_attivi(self):
        return self.persona.inviti_corsi.all().values_list('corso', flat=True)

    @classmethod
    def _anche_volontari(cls):
        volontari = Aspirante.objects.filter(
            persona__appartenenze__fine__isnull=True, persona__appartenenze__membro=Appartenenza.VOLONTARIO
        )
        return volontari

    @classmethod
    def _chiudi_partecipazioni(cls, qs):
        for partecipazione in PartecipazioneCorsoBase.objects.filter(persona__in=qs.values_list('persona', flat=True)):
            partecipazione.esito_esame = PartecipazioneCorsoBase.IDONEO
            partecipazione.ammissione = PartecipazioneCorsoBase.AMMESSO
            partecipazione.esito_parte_1 = PartecipazioneCorsoBase.POSITIVO
            partecipazione.esito_parte_2 = PartecipazioneCorsoBase.POSITIVO
            partecipazione.destinazione = partecipazione.persona.comitato_riferimento()
            partecipazione.save()

    @classmethod
    def pulisci_volontari(cls):
        volontari = cls._anche_volontari()
        cls._chiudi_partecipazioni(volontari)
        volontari.delete()


class RelazioneCorso(ModelloSemplice, ConMarcaTemporale):
    SENZA_VALORE = "Non ci sono segnalazioni e/o annotazioni"

    corso = models.ForeignKey(CorsoBase, related_name='relazione_corso')
    note_esplicative = models.TextField(
        blank=True, null=True,
        verbose_name='Note esplicative',
        help_text="Note esplicative in relazione ai cambiamenti effettuati rispetto "
                  "alla programmazione approvata in fase di pianificazione iniziale del corso.")
    raggiungimento_obiettivi = models.TextField(
        blank=True, null=True,
        verbose_name='Raggiungimento degli obiettivi del corso',
        help_text="Analisi sul raggiungimento degli obiettivi del corso "
                  "(generali rispetto all'evento e specifici di apprendimento).")
    annotazioni_corsisti = models.TextField(
        blank=True, null=True,
        verbose_name="Annotazioni relative alla partecipazione dei corsisti",
        help_text="Annotazioni relative alla partecipazione dei corsisti ")
    annotazioni_risorse = models.TextField(
        blank=True, null=True,
        help_text="Annotazioni relative a risorse e competenze di particolare "
                  "rilevanza emerse durante il percorso formativo")
    annotazioni_organizzazione_struttura = models.TextField(
        blank=True, null=True,
        help_text="Annotazioni e segnalazioni sull'organizzazione e "
                  "la logistica e della struttura ospitante il corso")
    descrizione_attivita = models.TextField(
        blank=True, null=True,
        help_text="Descrizione delle eventuali attività di "
                  "tirocinio/affiancamento con indicazione dei Tutor")

    @property
    def is_completed(self):
        if self.corso.esame_previsto == False:
            return True

        model_fields = self._meta.get_fields()
        super_class_fields_to_exclude = ['id', 'creazione', 'ultima_modifica', 'corso']
        fields = [i.name for i in model_fields if i.name not in super_class_fields_to_exclude]
        if list(filter(lambda x: x in ['', None], [getattr(self, i) for i in fields])):
            return False
        return True

    def __str__(self):
        return 'Relazione Corso <%s>' % self.corso.nome

    class Meta:
        verbose_name = 'Relazione del Direttore'
        verbose_name_plural = 'Relazioni dei Direttori'
