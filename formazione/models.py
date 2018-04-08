# coding=utf-8

"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from anagrafica.costanti import PROVINCIALE, TERRITORIALE, LOCALE
from anagrafica.models import Sede, Persona, Appartenenza
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI, INCARICO_ASPIRANTE
from base.files import PDF, Zip
from base.models import ConAutorizzazioni, ConVecchioID, Autorizzazione
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConDelegati, ConStorico, ConPDF
from base.utils import concept, poco_fa
from posta.models import Messaggio
from social.models import ConCommenti, ConGiudizio
from django.db import models


class Corso(ModelloSemplice, ConDelegati, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio):

    class Meta:
        abstract = True
        permissions = (
            ("view_corso", "Can view corso"),
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
    sede = models.ForeignKey(Sede, related_query_name='%(class)s_corso', help_text="La Sede organizzatrice del Corso.")


class CorsoBase(Corso, ConVecchioID, ConPDF):

    ## Tipologia di corso
    #BASE = 'BA'
    #TIPO = (
    #    (BASE, 'Corso Base'),
    #)
    #tipo = models.CharField('Tipo', choices=TIPO, max_length=2, default=BASE)

    MAX_PARTECIPANTI = 30

    class Meta:
        verbose_name = "Corso Base"
        verbose_name_plural = "Corsi Base"
        ordering = ['-anno', '-progressivo']
        permissions = (
            ("view_corsobase", "Can view corso base"),
        )

    data_inizio = models.DateTimeField(blank=False, null=False, help_text="La data di inizio del corso. "
                                                                          "Utilizzata per la gestione delle iscrizioni.")
    data_esame = models.DateTimeField(blank=False, null=False)
    progressivo = models.SmallIntegerField(blank=False, null=False, db_index=True)
    anno = models.SmallIntegerField(blank=False, null=False, db_index=True)
    descrizione = models.TextField(blank=True, null=True)

    data_attivazione = models.DateField(blank=True, null=True)
    data_convocazione = models.DateField(blank=True, null=True)
    op_attivazione = models.CharField(max_length=255, blank=True, null=True)
    op_convocazione = models.CharField(max_length=255, blank=True, null=True)

    PUOI_ISCRIVERTI_OK = "IS"
    PUOI_ISCRIVERTI = (PUOI_ISCRIVERTI_OK,)

    SEI_ISCRITTO_PUOI_RITIRARTI = "GIA"
    SEI_ISCRITTO_NON_PUOI_RITIRARTI = "NP"
    SEI_ISCRITTO = (SEI_ISCRITTO_PUOI_RITIRARTI, SEI_ISCRITTO_NON_PUOI_RITIRARTI,)

    NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO = "VOL"
    NON_PUOI_ISCRIVERTI_TROPPO_TARDI = "TAR"
    NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO = "ALT"
    NON_PUOI_ISCRIVERTI = (NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO, NON_PUOI_ISCRIVERTI_TROPPO_TARDI,
                           NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO,)

    NON_PUOI_ISCRIVERTI_SOLO_SE_IN_AUTONOMIA = (NON_PUOI_ISCRIVERTI_TROPPO_TARDI,)

    def persona(self, persona):
        if (not Aspirante.objects.filter(persona=persona).exists()) and persona.volontario:
            return self.NON_PUOI_ISCRIVERTI_GIA_VOLONTARIO

        if PartecipazioneCorsoBase.con_esito_ok(persona=persona, corso__stato=self.ATTIVO).exclude(corso=self).exists():
            return self.NON_PUOI_ISCRIVERTI_GIA_ISCRITTO_ALTRO_CORSO

        # Controlla se gia' iscritto.
        if PartecipazioneCorsoBase.con_esito_ok(persona=persona, corso=self).exists():
            return self.SEI_ISCRITTO_NON_PUOI_RITIRARTI

        if PartecipazioneCorsoBase.con_esito_pending(persona=persona, corso=self).exists():
            return self.SEI_ISCRITTO_PUOI_RITIRARTI

        if self.troppo_tardi_per_iscriverti:
            return self.NON_PUOI_ISCRIVERTI_TROPPO_TARDI

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
        """
        Concept per Corsi Base pubblici (attivi e non ancora iniziati...)
        """
        return Q(
            data_inizio__gte=timezone.now() - datetime.timedelta(days=settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI),
            stato=cls.ATTIVO
        )

    @property
    def iniziato(self):
        return self.data_inizio < timezone.now()

    @property
    def troppo_tardi_per_iscriverti(self):
        return timezone.now() > (self.data_inizio + datetime.timedelta(days=settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI))

    @property
    def possibile_aggiungere_iscritti(self):
        return self.stato in [Corso.ATTIVO, Corso.PREPARAZIONE]

    @property
    def possibile_cancellare_iscritti(self):
        return self.stato in [Corso.ATTIVO, Corso.PREPARAZIONE]

    def __str__(self):
        return self.nome

    @property
    def url(self):
        return "/aspirante/corso-base/%d/" % (self.pk,)

    @property
    def nome(self):
        return "Corso Base %d/%d (%s)" % (self.progressivo, self.anno, self.sede)

    @property
    def link(self):
        return "<a href=\"%s\">%s</a>" % (self.url, self.nome)

    @property
    def url_direttori(self):
        return "/formazione/corsi-base/%d/direttori/" % (self.pk,)

    @property
    def url_modifica(self):
        return "%smodifica/" % (self.url,)

    @property
    def url_attiva(self):
        return "%sattiva/" % (self.url,)

    @property
    def url_termina(self):
        return "%stermina/" % (self.url,)

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
        return "%smappa/" % (self.url,)

    @property
    def url_lezioni(self):
        return "%slezioni/" % (self.url,)

    @property
    def url_report(self):
        return "%sreport/" % (self.url,)

    @property
    def url_report_schede(self):
        return self.url + "report/schede/"

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
            ultimo = CorsoBase.objects.filter(anno=anno).latest('progressivo')
            progressivo = ultimo.progressivo + 1

        except:  # Se non esiste, inizia da 1
            progressivo = 1

        c = CorsoBase(
            anno=anno,
            progressivo=progressivo,
            **kwargs
        )
        c.save()
        return c

    def attivabile(self):
        """
        Controlla se il corso base e' attivabile.
        """

        if not self.locazione:
            return False

        if not self.descrizione:
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

    def attiva(self, rispondi_a=None):
        if not self.attivabile():
            raise ValueError("Questo corso non è attivabile.")

        self._invia_email_agli_aspiranti(rispondi_a=rispondi_a)
        self.stato = self.ATTIVO
        self.save()

    def _invia_email_agli_aspiranti(self, rispondi_a=None):
        for aspirante in self.aspiranti_nelle_vicinanze():
            persona = aspirante.persona
            if not aspirante.persona.volontario:
                Messaggio.costruisci_e_accoda(
                    oggetto="Nuovo Corso per Volontari CRI",
                    modello="email_aspirante_corso.html",
                    corpo={
                        "persona": persona,
                        "corso": self,
                    },
                    destinatari=[persona],
                    rispondi_a=rispondi_a
                )

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
        """
        Termina il corso base, genera il verbale e volontarizza.
        """

        from django.db import transaction
        with transaction.atomic():
            # Per maggiore sicurezza, questa cosa viene eseguita in una transazione.

            for partecipante in self.partecipazioni_confermate():

                # Calcola e salva l'esito dell'esame.
                esito_esame = partecipante.IDONEO if partecipante.idoneo else partecipante.NON_IDONEO
                partecipante.esito_esame = esito_esame
                partecipante.save()

                # Comunica il risultato all'aspirante/volontario.
                partecipante.notifica_esito_esame(mittente=mittente)

                if partecipante.idoneo:  # Se idoneo, volontarizza.
                    partecipante.persona.da_aspirante_a_volontario(sede=partecipante.destinazione,
                                                                   mittente=mittente)

            # Cancella tutte le eventuali partecipazioni in attesa.
            PartecipazioneCorsoBase.con_esito_pending(corso=self).delete()

            # Salva lo stato del corso come terminato.
            self.stato = Corso.TERMINATO
            self.save()

    def non_idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.NON_IDONEO)

    def idonei(self):
        return self.partecipazioni_confermate().filter(esito_esame=PartecipazioneCorsoBase.IDONEO)

    def genera_pdf(self):
        """
        Genera il verbale del corso.
        """
        if not self.ha_verbale:
            raise ValueError("Questo corso non ha un verbale.")

        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
            nome="Verbale Esame del Corso Base %d-%d.pdf" % (self.progressivo, self.anno),
            corpo={
                "corso": self,
                "partecipazioni": self.partecipazioni_confermate(),
                "numero_idonei": self.idonei().count(),
                "numero_non_idonei": self.non_idonei().count(),
                "numero_aspiranti": self.partecipazioni_confermate().count(),
            },
            modello="pdf_corso_base_esame_verbale.html",
        )
        return pdf


class InvitoCorsoBase(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale, models.Model):
    persona = models.ForeignKey(Persona, related_name='inviti_corsi', on_delete=models.CASCADE)
    corso = models.ForeignKey(CorsoBase, related_name='inviti', on_delete=models.PROTECT)
    invitante = models.ForeignKey(Persona, related_name='+', on_delete=models.CASCADE)

    # Stati per l'iscrizione da parte del direttore
    NON_ISCRITTO = 0
    ISCRITTO = 1
    IN_ATTESA_ASPIRANTE = 2
    INVITO_INVIATO = -1

    RICHIESTA_NOME = "iscrizione a Corso Base"

    APPROVAZIONE_AUTOMATICA = datetime.timedelta(days=settings.SCADENZA_AUTORIZZAZIONE_AUTOMATICA)

    class Meta:
        verbose_name = "Invito di partecipazione a corso base"
        verbose_name_plural = "Inviti di partecipazione a corso base"
        ordering = ('persona__cognome', 'persona__nome', 'persona__codice_fiscale',)
        permissions = (
            ("view_invitocorsobase", "Can view invito partecipazione corso base"),
        )

    def __str__(self):
        return "Invit di part. di %s a %s" % (
            self.persona, self.corso
        )

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
            oggetto="Annullamento invito al Corso Base: %s" % self.corso,
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
            oggetto="Annullamento invito al Corso Base: %s" % self.corso,
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

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"
        ordering = ('persona__cognome', 'persona__nome', 'persona__codice_fiscale',)
        permissions = (
            ("view_partecipazionecorsobarse", "Can view corso Richiesta di partecipazione"),
        )

    RICHIESTA_NOME = "Iscrizione Corso Base"

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
        """
        Invia una e-mail al partecipante con l'esito del proprio esame.
        """
        Messaggio.costruisci_e_accoda(
            oggetto="Esito del Corso Base: %s" % self.corso,
            modello="email_aspirante_corso_esito.html",
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
        """
        Disiscrive partecipante dal corso base.
        """
        self.autorizzazioni_ritira()
        Messaggio.costruisci_e_invia(
            oggetto="Disiscrizione dal Corso Base: %s" % self.corso,
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
            oggetto="Disiscrizione dal Corso Base: %s" % self.corso,
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

    def __str__(self):
        return "Richiesta di part. di %s a %s" % (
            self.persona, self.corso
        )

    def autorizzazione_concedi_modulo(self):
        from formazione.forms import ModuloConfermaIscrizioneCorsoBase
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


class LezioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConStorico):

    corso = models.ForeignKey(CorsoBase, related_name='lezioni', on_delete=models.PROTECT)
    nome = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Lezione di Corso Base"
        verbose_name_plural = "Lezioni di Corsi Base"
        ordering = ['inizio']
        permissions = (
            ("view_lezionecorsobase", "Can view corso Lezione di Corso Base"),
        )

    def __str__(self):
        return "Lezione: %s" % (self.nome,)

    @property
    def url_cancella(self):
        return "%s%d/cancella/" % (
            self.corso.url_lezioni, self.pk
        )


class AssenzaCorsoBase(ModelloSemplice, ConMarcaTemporale):

    lezione = models.ForeignKey(LezioneCorsoBase, related_name='assenze', on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, related_name='assenze_corsi_base', on_delete=models.CASCADE)
    registrata_da = models.ForeignKey(Persona, related_name='assenze_corsi_base_registrate', null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Assenza a Corso Base"
        verbose_name_plural = "Assenze ai Corsi Base"
        permissions = (
            ("view_assenzacorsobase", "Can view corso Assenza a Corso Base"),
        )

    def __str__(self):
        return "Assenza di %s a %s" % (
            self.persona.codice_fiscale, self.lezione
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

    def corso(self):
        return CorsoBase.objects.filter(
            PartecipazioneCorsoBase.con_esito_ok(persona=self.persona).via("partecipazioni"),
            stato=Corso.ATTIVO,
        ).first()

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
        return self.nel_raggio(CorsoBase.pubblici().filter(**kwargs))

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