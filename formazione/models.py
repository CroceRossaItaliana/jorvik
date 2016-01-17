# coding=utf-8

"""
Questo modulo definisce i modelli del modulo di Formazione di Gaia.
"""
import datetime

from django.db.models import Q
from django.utils import timezone

from anagrafica.models import Sede, Persona
from base.models import ConAutorizzazioni, ConVecchioID
from base.geo import ConGeolocalizzazione, ConGeolocalizzazioneRaggio
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConDelegati, ConStorico
from base.utils import concept
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

    @classmethod
    @concept
    def pubblici(cls):
        """
        Concept per Corsi Base pubblici (attivi e non ancora iniziati...)
        """
        return Q(data_inizio__gte=timezone.now(), stato=cls.ATTIVO)

    @property
    def iniziato(self):
        return self.data_inizio >= timezone.now()

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
    def url_attiva(self):
        return "%sattiva/" % (self.url,)

    @property
    def url_mappa(self):
        return "%smappa/" % (self.url,)

    @property
    def url_lezioni_modifica(self):
        return "%slezioni/" % (self.url,)

    @property
    def url_report(self):
        return "%sreport/" % (self.url,)

    @classmethod
    def nuovo(cls, anno=datetime.date.today().year, **kwargs):
        """
        Metodo per creare un nuovo corso. Crea progressivo automaticamente.
        :param anno: Anno di creazione del corso.
        :param kwargs: Parametri per la creazione del corso.
        :return:
        """

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

    def attiva(self):
        """
        Effettua l'attivazione del corso base.
        """
        self.stato = self.ATTIVO
        self.save()

    @property
    def aspiranti_nelle_vicinanze(self):
        from formazione.models import Aspirante
        return self.circonferenze_contenenti(Aspirante.objects.all()).count()

    def partecipazioni_confermate(self):
        return self.partecipazioni.all().filter(stato=PartecipazioneCorsoBase.CONFERMATA)

    def partecipazioni_in_attesa(self):
        return self.partecipazioni.all().filter(stato=PartecipazioneCorsoBase.IN_ATTESA)

    def partecipazioni_negate(self):
        return self.partecipazioni.all().filter(stato=PartecipazioneCorsoBase.NEGATA)


class PartecipazioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    persona = models.ForeignKey(Persona, related_name='partecipazioni_corsi')
    corso = models.ForeignKey(CorsoBase, related_name='partecipazioni')

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
    esito_esame = models.CharField(max_length=2, choices=ESITO_IDONEO, default=None, null=True, db_index=True)

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

    esito_parte_1 = models.CharField(max_length=1, choices=ESITO, default=None, null=True, db_index=True,
                                     help_text="La Croce Rossa")
    argomento_parte_1 = models.TextField(max_length=1024, blank=True, null=True, help_text="es. Storia della CRI, DIU")

    esito_parte_2 = models.CharField(max_length=1, choices=ESITO, default=None, null=True, db_index=True,
                                     help_text="Gesti e manovre salvavita")
    argomento_parte_2 = models.TextField(max_length=1024, blank=True, null=True, help_text="es. BLS, colpo di calore")

    extra_1 = models.BooleanField(help_text="Prova pratica su Parte 2 sostituita da colloquio.", default=False)
    extra_2 = models.BooleanField(help_text="Verifica effettuata solo sulla Parte 1 del programma del corso.",
                                  default=False)

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"


class LezioneCorsoBase(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConStorico):

    corso = models.ForeignKey(CorsoBase, related_name='lezioni')
    nome = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Lezione di Corso Base"
        verbose_name_plural = "Lezioni di Corsi Base"


class AssenzaCorsoBase(ModelloSemplice, ConMarcaTemporale):

    lezione = models.ForeignKey(LezioneCorsoBase, related_name='assenze')
    persona = models.ForeignKey(Persona, related_name='assenze_corsi_base')
    registrata_da = models.ForeignKey(Persona, related_name='assenze_corsi_base_registrate')

    class Meta:
        verbose_name = "Assenza a Corso Base"
        verbose_name_plural = "Assenze ai Corsi Base"


class Aspirante(ModelloSemplice, ConGeolocalizzazioneRaggio, ConMarcaTemporale):

    persona = models.OneToOneField(Persona, related_name='aspirante')

    # Numero minimo di Comitati nelle vicinanze
    MINIMO_COMITATI = 15
    RAGGIO_STEP = 1.4

    # Massimo iterazioni nella ricerca
    MASSIMO_ITERAZIONI = 50

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
        iterazione = 0
        self.raggio = .0
        while True:
            iterazione += 1
            self.raggio += self.RAGGIO_STEP
            self.save()

            if iterazione >= self.MASSIMO_ITERAZIONI or self.sedi().count() >= self.MINIMO_COMITATI:
                break

        return self.raggio

    def post_locazione(self):
        """
        Ricalcola il raggio automaticamente ogni volta che viene impostata
        una nuova locazione.
        """
        self.calcola_raggio()
        return super(Aspirante, self).post_locazione()
