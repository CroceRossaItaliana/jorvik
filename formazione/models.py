import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Q
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from anagrafica.models import Sede, Persona, Appartenenza, Delega
from anagrafica.costanti import PROVINCIALE, TERRITORIALE, LOCALE, REGIONALE, NAZIONALE
from anagrafica.validators import (valida_dimensione_file_8mb, ValidateFileSize)
from anagrafica.permessi.applicazioni import DIRETTORE_CORSO
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
from posta.models import Messaggio
from social.models import ConCommenti, ConGiudizio
from survey.models import Survey
from .validators import (course_file_directory_path, validate_file_extension,
                         delibera_file_upload_path)


class Corso(ModelloSemplice, ConDelegati, ConMarcaTemporale,
            ConGeolocalizzazione, ConCommenti, ConGiudizio):
    # Tipologia di corso
    CORSO_NUOVO = 'C1'
    BASE = 'BA'
    TIPO_CHOICES = (
        (BASE, 'Corso di Formazione per Volontari CRI'),
        (CORSO_NUOVO, 'Altri Corsi'),
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


class CorsoLink(models.Model):
    is_enabled = models.BooleanField(default=True)
    corso = models.ForeignKey('CorsoBase')
    link = models.URLField('Link', null=True, blank=True)

    def __str__(self):
        corso = self.corso if hasattr(self, 'corso') else ''
        return '<%s> of %s' % (self.link, corso)


class CorsoBase(Corso, ConVecchioID, ConPDF):
    from django.core.validators import MinValueValidator

    MIN_PARTECIPANTI = 20
    MAX_PARTECIPANTI = 50

    EXT_MIA_SEDE        = '1'
    EXT_LVL_REGIONALE   = '2'
    EXTENSION_TYPE_CHOICES = [
        (EXT_MIA_SEDE, "Solo su mia sede di appartenenza"),
        (EXT_LVL_REGIONALE, "A livello regionale"),
    ]

    data_inizio = models.DateTimeField(blank=False, null=False,
        help_text="La data di inizio del corso. "
                  "Utilizzata per la gestione delle iscrizioni.")
    data_esame = models.DateTimeField(blank=False, null=False)
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
        validators=[ValidateFileSize(3), validate_file_extension]
    )
    titolo_cri = models.ForeignKey(Titolo, blank=True, null=True,
                                   verbose_name="Titolo CRI")
    cdf_level = models.CharField(max_length=3, choices=Titolo.CDF_LIVELLI,
                                 null=True, blank=True)
    cdf_area = models.CharField(max_length=3, choices=OBBIETTIVI_STRATEGICI,
                                 null=True, blank=True)
    survey = models.ForeignKey(Survey, blank=True, null=True,
                               verbose_name='Questionario di gradimento')

    PUOI_ISCRIVERTI_OK = "IS"
    PUOI_ISCRIVERTI = (PUOI_ISCRIVERTI_OK,)

    SEI_ISCRITTO_PUOI_RITIRARTI = "GIA"
    SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI = "IPC"
    SEI_ISCRITTO_NON_PUOI_RITIRARTI = "NP"
    SEI_ISCRITTO = (SEI_ISCRITTO_PUOI_RITIRARTI,
                    SEI_ISCRITTO_CONFERMATO_PUOI_RITIRARTI,)

    NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO = "VOL"
    NON_PUOI_ISCRIVERTI_TROPPO_TARDI = "TAR"
    NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO = "ALT"
    NON_PUOI_SEI_ASPIRANTE = 'ASP'
    NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI = 'NHT'
    NON_HAI_CARICATO_DOCUMENTI_PERSONALI = 'NHCDP'
    NON_HAI_DOCUMENTO_PERSONALE_VALIDO = 'NHDPV'
    NON_PUOI_ISCRIVERTI = (NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO,
                           NON_PUOI_ISCRIVERTI_TROPPO_TARDI,
                           # NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO,
                           NON_PUOI_SEI_ASPIRANTE,
                           NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI,
                           NON_HAI_CARICATO_DOCUMENTI_PERSONALI,
                           NON_HAI_DOCUMENTO_PERSONALE_VALIDO)

    NON_PUOI_ISCRIVERTI_SOLO_SE_IN_AUTONOMIA = (NON_PUOI_ISCRIVERTI_TROPPO_TARDI,)

    def persona(self, persona):
        # Checks related to tipo.CORSO_NUOVO (not old CorsoBase)
        if Corso.CORSO_NUOVO == self.tipo:
            if persona.ha_aspirante:
                return self.NON_PUOI_SEI_ASPIRANTE

            # if not persona.has_required_titles_for_course(course=self):
            #     return self.NON_PUOI_ISCRIVERTI_NON_HAI_TITOLI

        # if (not Aspirante.objects.filter(persona=persona).exists()) and persona.volontario:
        #     return self.NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO

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

    def possibili_destinazioni(self):
        """
        Ritorna le possibili destinazioni per l'iscrizione dei Volontari.
        """
        return self.sede.comitato.espandi(includi_me=True)

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
    def find_courses_for_volunteer(cls, volunteer):
        today = datetime.date.today()
        sede = volunteer.sedi_attuali(membro=Appartenenza.VOLONTARIO)
        if not sede:
            return cls.objects.none()  # corsi non trovati perchè utente non ha sede

        ###
        # Trova corsi che hanno <sede> uguale alla <sede del volontario>
        ###
        qs_estensioni_1 = CorsoEstensione.objects.filter(sede__in=sede,
                                                         corso__tipo=Corso.CORSO_NUOVO,
                                                         corso__stato=Corso.ATTIVO,
                                                         corso__data_inizio__gt=today)
        courses_1 = cls.objects.filter(id__in=qs_estensioni_1.values_list('corso__id'))

        ###
        # Trova corsi dove la <sede del volontario> si verifica come sede sottostante
        ###
        four_weeks_delta = today + datetime.timedelta(weeks=4)
        qs_estensioni_2 = CorsoEstensione.objects.filter(
            corso__tipo=Corso.CORSO_NUOVO,
            corso__stato=Corso.ATTIVO,
            corso__data_inizio__gt=today,
            corso__data_esame__lt=four_weeks_delta).exclude(
            corso__id__in=courses_1.values_list('id', flat=True))

        courses_2 = list()
        for estensione in qs_estensioni_2:
            for s in estensione.sede.all():
                sedi_sottostanti = s.esplora()
                for _ in sede:
                    if _ in sedi_sottostanti:
                        _corso = estensione.corso
                        if _corso not in courses_2:
                                courses_2.append(_corso.pk)

        courses_2 = cls.objects.filter(id__in=courses_2)

        return courses_1 | courses_2

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
        return "/aspirante/corso-base/%d/" % (self.pk,)

    @property
    def nome(self):
        course_type = 'Corso Base' if self.tipo == Corso.BASE else 'Corso'
        return "%s %d/%d (%s)" % (course_type, self.progressivo, self.anno, self.sede)

    @property
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url, self.nome)

    @property
    def url_direttori(self):
        return "/formazione/corsi-base/%d/direttori/" % (self.pk,)

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
        c.save()
        return c

    def attivabile(self):
        """Controlla se il corso base e' attivabile."""

        if not self.locazione:
            return False

        if not self.descrizione:
            return False

        if self.is_nuovo_corso and self.extension_type != CorsoBase.EXT_LVL_REGIONALE:
            return False

        if self.direttori_corso().count() == 0:
            return False

        return True

    def aspiranti_nelle_vicinanze(self):
        from formazione.models import Aspirante
        return self.circonferenze_contenenti(Aspirante.query_contattabili())

    def partecipazioni_confermate_o_in_attesa(self):
        return self.partecipazioni_confermate() | self.partecipazioni_in_attesa()

    def partecipazioni_confermate(self):
        return PartecipazioneCorsoBase.con_esito_ok(corso=self)

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

        if self.is_nuovo_corso:
            messaggio = "A breve tutti i volontari dei segmenti selezionati "\
                        "verranno informati dell'attivazione di questo corso."
        else:
            messaggio = "A breve tutti gli aspiranti nelle vicinanze verranno "\
                        "informati dell'attivazione di questo corso base."

        self.stato = self.ATTIVO
        self.save()

        task_invia_email_agli_aspiranti.apply_async(args=(self.pk, rispondi_a.pk),)

        return messaggio_generico(request, rispondi_a,
            titolo="Corso attivato con successo",
            messaggio=messaggio,
            torna_titolo="Torna al Corso",
            torna_url=self.url)

    def _corso_activation_recipients_for_email(self):
        if self.is_nuovo_corso:
            recipients = self.get_volunteers_by_course_requirements()
        else:
            recipients = self.aspiranti_nelle_vicinanze()
        return recipients

    def _invia_email_agli_aspiranti(self, rispondi_a=None):
        for recipient in self._corso_activation_recipients_for_email():
            if self.is_nuovo_corso:
                persona = recipient
                subject = "Nuovo Corso %s per Volontari CRI" % self.titolo_cri
            else:
                persona = recipient.persona
                subject = "Nuovo Corso per Volontari CRI"

            email_data = dict(
                oggetto=subject,
                modello="email_aspirante_corso.html",
                corpo={
                    'persona': persona,
                    'corso': self,
                },
                destinatari=[persona],
                rispondi_a=rispondi_a
            )

            if self.is_nuovo_corso:
                # If course tipo is CORSO_NUOVO to send to volunteers only
                Messaggio.costruisci_e_accoda(**email_data)
            elif not self.is_nuovo_corso and not recipient.persona.volontario:
                # to send to <Aspirante> only
                Messaggio.costruisci_e_accoda(**email_data)

    def has_extensions(self, is_active=True, **kwargs):
        """ Case: extension_type == EXT_LVL_REGIONALE """
        return self.corsoestensione_set.filter(is_active=is_active).exists()

    def get_extensions(self, **kwargs):
        """ Returns CorsoEstensione objects related to the course """
        return self.corsoestensione_set.filter(**kwargs)

    def get_extensions_sede(self, with_expanded=True, **kwargs):
        """ Returns SedeQuerySet """
        if with_expanded:
            return self.expand_extensions_sedi_sottostanti()
        else:
            return CorsoEstensione.get_sede(course=self, **kwargs)

    def expand_extensions_sedi_sottostanti(self):
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
        persons = None

        if self.is_nuovo_corso:
            corso_extension = self.extension_type
            if CorsoBase.EXT_MIA_SEDE == corso_extension:
                persons = self.get_volunteers_by_only_sede()

            if CorsoBase.EXT_LVL_REGIONALE == corso_extension:
                by_ext_sede = self.get_volunteers_by_ext_sede()
                by_ext_titles = self.get_volunteers_by_ext_titles()
                persons = by_ext_sede | by_ext_titles

        if persons is None:
            # Sede of course (was set in the first step of course creation)
            persons = Persona.objects.filter(sede=self.sede)

        return persons.filter(**kwargs).distinct()

    @property
    def get_firmatario(self):
        last = self.deleghe.last()
        return last.firmatario if hasattr(last, 'firmatario') else last

    @property
    def get_firmatario_sede(self):
        course_created_by = self.get_firmatario
        if course_created_by is not None:
            return course_created_by.sede_riferimento()
        else:
            return course_created_by # returns None

    def get_volunteers_by_only_sede(self):
        app_attuali = Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO).q
        app = Appartenenza.objects.filter(app_attuali,
                                          sede=self.get_firmatario_sede,
                                          confermata=True)
        return self._query_get_volunteers_by_sede(app)

    def get_volunteers_by_ext_sede(self):
        app_attuali = Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO).q
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

    @property
    def concluso(self):
        return timezone.now() >= self.data_esame

    @property
    def terminabile(self):
        return self.stato == self.ATTIVO and self.concluso and self.partecipazioni_confermate().exists()

    @property
    def ha_verbale(self):
        return self.stato == self.TERMINATO and self.partecipazioni_confermate().exists()

    def termina(self, mittente=None):
        """ Termina il corso base, genera il verbale e volontarizza. """

        with transaction.atomic():
            # Per maggiore sicurezza, questa cosa viene eseguita in una transazione

            for partecipante in self.partecipazioni_confermate():
                # Calcola e salva l'esito dell'esame.
                esito_esame = partecipante.IDONEO if partecipante.idoneo \
                                                else partecipante.NON_IDONEO
                partecipante.esito_esame = esito_esame
                partecipante.save()

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

            # Salva lo stato del corso come terminato
            self.stato = Corso.TERMINATO
            self.save()

        if self.is_nuovo_corso:
            self.set_titolo_cri_to_participants()

    def set_titolo_cri_to_participants(self):
        """ Sets <titolo_cri> in Persona's Curriculum (TitoloPersonale) """

        from curriculum.models import TitoloPersonale

        objs = [
            TitoloPersonale(
                confermata=True,
                titolo=self.titolo_cri,
                persona=p.persona,
                certificato_da=self.get_firmatario,
                data_scadenza=timezone.now() + self.titolo_cri.expires_after_timedelta,
                is_course_title=True,
                corso_partecipazione=p,

                # todo: attending details
                # data_ottenimento='',
                # luogo_ottenimento='',
                # codice='',
                # codice_corso='',
                # certificato='',
            )
            for p in self.partecipazioni_confermate()
        ]
        TitoloPersonale.objects.bulk_create(objs)

    def non_idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.NON_IDONEO)

    def idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.IDONEO)

    def genera_pdf_firme(self):
        """
        Genera il fogli firme delle lezioni del corso.
        """
        def key_cognome(elem):
           return elem.cognome

        iscritti = [partecipazione.persona for partecipazione in self.partecipazioni_confermate()]

        archivio = Zip(oggetto=self)
        for lezione in self.lezioni.all():

            pdf = PDF(oggetto=self)
            pdf.genera_e_salva(
                nome="Firme lezione %s.pdf" % lezione.nome,
                corpo={
                    "corso": self,
                    "iscritti": sorted(iscritti, key=key_cognome),
                    "lezione": lezione,
                    "data": lezione.inizio,
                },
                modello="pdf_firme_lezione.html",
            )
            archivio.aggiungi_file(file_path=pdf.file.path, nome_file=pdf.nome)

        archivio.comprimi_e_salva(nome="Fogli firme %s.zip" % self.nome)

        return archivio

    def genera_pdf(self):
        """
        Genera il verbale del corso.
        """
        def key_cognome(elem):
            return elem.persona.cognome

        if not self.ha_verbale:
            raise ValueError("Questo corso non ha un verbale.")

        partecipazioni = self.partecipazioni_confermate()
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
            nome="Verbale Esame del Corso Base %d-%d.pdf" % (self.progressivo, self.anno),
            corpo={
                "corso": self,
                "partecipazioni": sorted(partecipazioni, key=key_cognome),
                "numero_idonei": self.idonei().count(),
                "numero_non_idonei": self.non_idonei().count(),
                "numero_aspiranti": self.partecipazioni_confermate().count(),
            },
            modello="pdf_corso_base_esame_verbale.html",
        )
        return pdf

    @property
    def is_reached_max_participants_limit(self):
        actual_requests = PartecipazioneCorsoBase.objects.filter(corso=self)
        return self.max_participants + 10 == actual_requests

    @property
    def is_nuovo_corso(self):
        return self.tipo == Corso.CORSO_NUOVO

    def get_course_links(self):
        return self.corsolink_set.filter(is_enabled=True)

    def get_course_files(self):
        return self.corsofile_set.filter(is_enabled=True)

    def inform_presidency_with_delibera_file(self):
        sede = self.sede.estensione
        email_body = """<p>E' stato attivato un nuovo corso. La delibera si trova in allegato.</p>"""

        if sede == LOCALE:
            # Corso in una sede Locale. - Informa presidenta della Sede
            email_to = self.sede.presidente().email
        elif sede in [REGIONALE, NAZIONALE]:
            # Corso in una sede Regionale/Nazionale. - Informa sulla mail
            email_to = 'formazione@cri.it'

        Messaggio.invia_raw(
            oggetto="Delibera nuovo corso: %s" % self,
            corpo_html=email_body,
            email_mittente=Messaggio.NOREPLY_EMAIL,
            lista_email_destinatari=[email_to,],
            allegati=self.delibera_file
        )

    def direttori_corso(self):
        oggetto_tipo = ContentType.objects.get_for_model(self)
        deleghe = Delega.objects.filter(tipo=DIRETTORE_CORSO,
                                        oggetto_tipo=oggetto_tipo.pk,
                                        oggetto_id=self.pk)
        deleghe_persone_id = deleghe.values_list('persona__id', flat=True)
        persone_qs = Persona.objects.filter(id__in=deleghe_persone_id)
        return persone_qs

    def can_modify(self, me):
        if me and me.permessi_almeno(self, MODIFICA):
            return True
        return False

    def can_activate(self, me):
        if me.is_presidente:
            """ All'presidente deve sparire la sezione dell'attivazione corso se:
            - ha caricato delibera
            - ha impostato estensioni (/aspirante/corso-base/<id>/estensioni/)
            - ha nominato almeno un direttore
            """
            has_delibera = self.delibera_file is not None
            has_extension = self.has_extensions()
            has_directors = self.direttori_corso().count() > 0
            is_all_true = has_delibera, has_extension, has_directors

            # # Deve riapparire se: il direttore ha inserito la descrizione
            # if self.descrizione:
            #     return True
            # else:
            return True if False in is_all_true else False
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
    from segmenti.segmenti import NOMI_SEGMENTI
    from curriculum.models import Titolo

    corso = models.ForeignKey(CorsoBase, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    segmento = models.CharField(max_length=9, choices=NOMI_SEGMENTI, blank=True)
    titolo = models.ManyToManyField(Titolo, blank=True)
    sede = models.ManyToManyField(Sede)
    sedi_sottostanti = models.BooleanField(default=False, db_index=True)

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


class PartecipazioneCorsoBase(ModelloSemplice, ConMarcaTemporale,
                              ConAutorizzazioni, ConPDF):

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
    ESITO = (
        (POSITIVO, "Positivo"),
        (NEGATIVO, "Negativo")
    )

    IDONEO = "OK"
    NON_IDONEO = "NO"
    ESITO_IDONEO = (
        (IDONEO, "Idoneo"),
        (NON_IDONEO, "Non Idoneo")
    )
    esito_esame = models.CharField(max_length=2, choices=ESITO_IDONEO, default=None, blank=True, null=True, db_index=True)

    AMMESSO = "AM"
    NON_AMMESSO = "NA"
    ASSENTE = "AS"
    AMMISSIONE = (
        (AMMESSO, "Ammesso"),
        (NON_AMMESSO, "Non Ammesso"),
        (ASSENTE, "Assente"),
    )

    ammissione = models.CharField(max_length=2, choices=AMMISSIONE, default=None, blank=True, null=True, db_index=True)
    motivo_non_ammissione = models.CharField(max_length=1025, blank=True, null=True)

    esito_parte_1 = models.CharField(max_length=1, choices=ESITO, default=None, blank=True, null=True, db_index=True,
                                     help_text="La Croce Rossa.")
    argomento_parte_1 = models.CharField(max_length=1024, blank=True, null=True, help_text="es. Storia della CRI, DIU.")

    esito_parte_2 = models.CharField(max_length=1, choices=ESITO, default=None, blank=True, null=True, db_index=True,
                                     help_text="Gesti e manovre salvavita.")
    argomento_parte_2 = models.CharField(max_length=1024, blank=True, null=True, help_text="es. BLS, colpo di calore.")

    extra_1 = models.BooleanField(verbose_name="Prova pratica su Parte 2 sostituita da colloquio.", default=False)
    extra_2 = models.BooleanField(verbose_name="Verifica effettuata solo sulla Parte 1 del programma del corso.",
                                  default=False)

    destinazione = models.ForeignKey("anagrafica.Sede", verbose_name="Sede di destinazione",
                                     related_name="aspiranti_destinati", default=None, null=True, blank=True,
                                     help_text="La Sede presso la quale verrà registrato come Volontario l'aspirante "
                                               "nel caso di superamento dell'esame.")

    RICHIESTA_NOME = "Iscrizione Corso"

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        # Quando un aspirante viene iscritto, tutte le richieste presso altri corsi devono essere cancellati.

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
        """
        Regole per l'idoneita'.
        """
        return (
            self.esito_parte_1 == self.POSITIVO and (
                self.esito_parte_2 == self.POSITIVO or (
                        self.extra_2 and not self.esito_parte_2
                    )
            )
        )

    def notifica_esito_esame(self, mittente=None):
        """ Invia una e-mail al partecipante con l'esito del proprio esame. """

        template = "email_%s_corso_esito.html"
        if self.corso.is_nuovo_corso:
            template = template % 'volontario'
        else:
            template = template % 'aspirante'

        Messaggio.costruisci_e_accoda(
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
        from formazione.forms import (ModuloConfermaIscrizioneCorsoBase,
                                      ModuloConfermaIscrizioneCorso)
        if self.corso.is_nuovo_corso:
            return ModuloConfermaIscrizioneCorso
        else:
            return ModuloConfermaIscrizioneCorsoBase

    def genera_scheda_valutazione(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
            nome="Scheda Valutazione %s.pdf" % self.persona.codice_fiscale,
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
            },
            modello="pdf_corso_base_scheda_valutazione.html",
        )
        return pdf

    def genera_attestato(self):
        if not self.idoneo:
            return None
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
            nome="Attestato %s.pdf" % self.persona.codice_fiscale,
            corpo={
                "partecipazione": self,
                "corso": self.corso,
                "persona": self.persona,
            },
            modello="pdf_corso_base_attestato.html",
        )
        return pdf

    def genera_pdf(self):
        z = Zip(oggetto=self)
        z.aggiungi_file(self.genera_scheda_valutazione().file.path)
        if self.idoneo:
            z.aggiungi_file(self.genera_attestato().file.path)
        z.comprimi_e_salva("%s.zip" % self.persona.codice_fiscale)
        return z

    @classmethod
    def controlla_richiesta_processabile(cls, richiesta):
        tipo = ContentType.objects.get_for_model(cls)
        if richiesta.oggetto_tipo != tipo:
            return True
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
    nome = models.CharField(max_length=128)
    docente = models.ForeignKey(Persona, null=True, default='',
                                verbose_name='Docente della lezione',)
    obiettivo = models.CharField('Obiettivo formativo della lezione',
                                 max_length=128, null=True, default='')
    luogo = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="il luogo di dove si svolgeranno le lezioni",
                             help_text="Compilare nel caso il luogo è diverso "
                                       "dal comitato che ha organizzato il corso.")

    @property
    def url_cancella(self):
        return "%s%d/cancella/" % (self.corso.url_lezioni, self.pk)

    def send_messagge_to_docente(self, me):
        Messaggio.costruisci_e_invia(
            oggetto='Lezione al %s' % self.corso.nome,
            modello="email_docente_assegnato_a_corso.html",
            corpo={
                "persona": self.docente,
                "corso": self.corso,
            },
            mittente=me,
            destinatari=[self.docente]
        )

    class Meta:
        verbose_name = "Lezione di Corso"
        verbose_name_plural = "Lezioni di Corsi"
        ordering = ['inizio']
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
        assenza, created = cls.objects.get_or_create(lezione=lezione,
                                                     persona=persona,
                                                     registrata_da=registrata_da)
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
        return self.nel_raggio(corsi)

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
