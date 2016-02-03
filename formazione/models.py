# coding=utf-8

"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
import datetime

from django.db.models import Q
from django.utils import timezone

from anagrafica.costanti import PROVINCIALE, TERRITORIALE, LOCALE
from anagrafica.models import Sede, Persona
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI
from base.models import ConAutorizzazioni, ConVecchioID
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConDelegati, ConStorico
from base.utils import concept
from posta.models import Messaggio
from social.models import ConCommenti, ConGiudizio
from django.db import models


class Corso(ModelloSemplice, ConDelegati, ConMarcaTemporale, ConGeolocalizzazione, ConCommenti, ConGiudizio):

    class Meta:
        abstract = True

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


class CorsoBase(Corso, ConVecchioID):

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

    def persona(self, persona):
        if not Aspirante.objects.filter(persona=persona).exists():
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

    @classmethod
    @concept
    def pubblici(cls):
        """
        Concept per Corsi Base pubblici (attivi e non ancora iniziati...)
        """
        return Q(data_inizio__gte=timezone.now(), stato=cls.ATTIVO)

    @property
    def iniziato(self):
        return self.data_inizio < timezone.now()

    @property
    def troppo_tardi_per_iscriverti(self):
        return timezone.now() > (self.data_inizio + datetime.timedelta(days=7))

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
        return "<a href=\"%s\" target=\"_new\">%s</a>" % (self.url, self.nome)

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
    def url_iscritti(self):
        return "%siscritti/" % (self.url,)

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
        return self.circonferenze_contenenti(Aspirante.objects.all())

    def partecipazioni_confermate_o_in_attesa(self):
        return self.partecipazioni_confermate() | self.partecipazioni_in_attesa()

    def partecipazioni_confermate(self):
        return PartecipazioneCorsoBase.con_esito_ok().filter(corso=self)

    def partecipazioni_in_attesa(self):
        return PartecipazioneCorsoBase.con_esito_pending().filter(corso=self)

    def partecipazioni_negate(self):
        return PartecipazioneCorsoBase.con_esito_no().filter(corso=self)

    def partecipazioni_ritirate(self):
        return PartecipazioneCorsoBase.con_esito_ritirata().filter(corso=self)

    def attiva(self):
        if not self.attivabile():
            raise ValueError("Questo corso non è attivabile.")

        self._invia_email_agli_aspiranti()
        self.stato = self.ATTIVO
        self.save()

    def _invia_email_agli_aspiranti(self):
        for aspirante in self.aspiranti_nelle_vicinanze():
            persona = aspirante.persona
            Messaggio.costruisci_e_accoda(
                oggetto="Nuovo Corso per Volontari CRI",
                modello="email_aspirante_corso.html",
                corpo={
                    "persona": persona,
                    "corso": self,
                },
                destinatari=[persona],
            )


class PartecipazioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    persona = models.ForeignKey(Persona, related_name='partecipazioni_corsi', on_delete=models.CASCADE)
    corso = models.ForeignKey(CorsoBase, related_name='partecipazioni', on_delete=models.PROTECT)

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
                                     help_text="La Croce Rossa")
    argomento_parte_1 = models.TextField(max_length=1024, blank=True, null=True, help_text="es. Storia della CRI, DIU")

    esito_parte_2 = models.CharField(max_length=1, choices=ESITO, default=None, blank=True,null=True, db_index=True,
                                     help_text="Gesti e manovre salvavita")
    argomento_parte_2 = models.TextField(max_length=1024, blank=True, null=True, help_text="es. BLS, colpo di calore")

    extra_1 = models.BooleanField(help_text="Prova pratica su Parte 2 sostituita da colloquio.", default=False)
    extra_2 = models.BooleanField(help_text="Verifica effettuata solo sulla Parte 1 del programma del corso.",
                                  default=False)

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"

    RICHIESTA_NOME = "Iscrizione Corso Base"

    def autorizzazione_concessa(self, modulo=None):
        # Quando un aspirante viene iscritto, tutte le richieste presso altri corsi devono essere cancellati.

        # Cancella tutte altre partecipazioni con esito pending - ce ne puo' essere solo una.
        PartecipazioneCorsoBase.con_esito_pending(persona=self.persona).exclude(corso=self.corso).delete()

    def ritira(self):
        self.autorizzazioni_ritira()

    def richiedi(self):
        self.autorizzazione_richiedi(
            self.persona,
                (
                    (INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI, self.corso)
                ),
            invia_notifiche=self.corso.delegati_attuali(),
        )

    def __str__(self):
        return "Richiesta di part. di %s a %s" % (
            self.persona, self.corso
        )


class LezioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConStorico):

    corso = models.ForeignKey(CorsoBase, related_name='lezioni', on_delete=models.PROTECT)
    nome = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Lezione di Corso Base"
        verbose_name_plural = "Lezioni di Corsi Base"
        ordering = ['inizio']

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
