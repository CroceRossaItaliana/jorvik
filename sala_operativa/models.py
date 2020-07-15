from datetime import timedelta
from math import floor, ceil

from django.db import models
from django.db.models import Q, F, Sum
from django.core.urlresolvers import reverse
from django.utils import timezone

from anagrafica.permessi.costanti import GESTIONE_SERVIZI


# todo: nuovo incarico
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI
# todo:

from base.utils import concept
from jorvik import settings
from anagrafica.models import Persona, Appartenenza, Sede
from anagrafica.permessi.applicazioni import REFERENTE_SO
from anagrafica.costanti import (LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, )
from attivita.models import AttivitaAbstract, PartecipazioneAbstract
from base.models import ModelloSemplice, Autorizzazione
from base.tratti import ConMarcaTemporale, ConStorico, ConDelegati
from social.models import ConGiudizio


class ServizioSO(AttivitaAbstract, ConStorico):
    BOZZA = 'B'
    VISIBILE = 'V'
    STATO = (
        (BOZZA, "Bozza"),
        (VISIBILE, "Visibile")
    )

    CHIUSA = 'C'
    APERTA = 'A'
    APERTURA = (
        (CHIUSA, 'Chiusa'),
        (APERTA, 'Aperta')
    )

    nome = models.CharField(max_length=255, default="Nuovo servizio", db_index=True)
    sede = models.ForeignKey('anagrafica.Sede', related_name='servizio', on_delete=models.PROTECT)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None,
        related_name='servizio_estensione', on_delete=models.PROTECT)
    stato = models.CharField(choices=STATO, default=BOZZA, max_length=1, db_index=True)
    apertura = models.CharField(choices=APERTURA, default=APERTA, max_length=1, db_index=True)
    descrizione = models.TextField(blank=True)

    @property
    def url(self):
        return reverse('so:scheda', args=[self.pk, ])

    @property
    def url_cancella(self):
        return reverse('so:scheda_cancella', args=[self.pk, ])

    @property
    def url_cancella_gruppo(self):
        return reverse('so:cancella_gruppo', args=[self.pk, ])

    @property
    def url_mezzi_materiali(self):
        return reverse('so:scheda_mm', args=[self.pk, ])

    def referenti_attuali(self, al_giorno=None):
        return self.delegati_attuali(tipo=REFERENTE_SO, al_giorno=al_giorno)

    def invia_ordine_di_partenza(self):
        pass

    def ore_uomo_di_servizio(self, solo_turni_passati=True):
        """
        Calcola e ritorna il numero di ore di servizio per uomo
        :return: timedelta
        """
        turni = self.turni_passati() if solo_turni_passati else self.turni.all()
        p = PartecipazioneSO.con_esito_ok(turno__attivita=self).annotate(
            durata=F('turno__fine') - F('turno__inizio'))
        a = p.aggregate(totale_ore=Sum('durata'))
        try:
            return a['totale_ore']
        except KeyError:
            return timedelta(minutes=0)

    def pagina_turni_oggi(self):
        posizione = TurnoSO.objects.filter(
            attivita=self,
            fine__lte=timezone.now(),
        ).count()
        return max(ceil(posizione / TurnoSO.PER_PAGINA), 1)

    def turni_futuri(self, *args, **kwargs):
        return TurnoSO.query_futuri(*args, attivita=self, **kwargs)

    def turni_passati(self, *args, **kwargs):
        return TurnoSO.query_passati(*args, attivita=self, **kwargs)

    def __str__(self):
        return str(self.nome)

    class Meta:
        verbose_name = 'Servizio'
        verbose_name_plural = 'Servizi'


class ReperibilitaSO(ModelloSemplice, ConMarcaTemporale, ConStorico):
    ESTENSIONE_CHOICES = (
        (LOCALE, 'Sede Locale'),
        (PROVINCIALE, 'Sede Provinciale'),
        (REGIONALE, 'Sede Regionale'),
        (NAZIONALE, 'Sede Nazionale')
    )

    attivazione = models.TimeField("Tempo di attivazione", default="00:15",
        help_text="Tempo necessario all'attivazione, in formato HH:mm.",)
    estensione = models.CharField(choices=ESTENSIONE_CHOICES, max_length=2)
    persona = models.ForeignKey(Persona, related_name="so_reperibilita", on_delete=models.CASCADE)
    # servizio = models.ManyToManyField(ServizioSO, blank=True)
    creato_da = models.ForeignKey(Persona, null=True, blank=True)

    @classmethod
    def reperibilita_di(cls, persona):
        return cls.objects.filter(persona=persona)

    @classmethod
    def reperibilita_create_da(cls, persona):
        return cls.objects.filter(creato_da=persona)

    @classmethod
    def reperibilita_per_sedi(cls, sedi):
        q = cls.query_attuale(
            Appartenenza.query_attuale(sede__in=sedi).via("persona__appartenenze"),
        ).order_by('attivazione', '-creazione')
        return cls.objects.filter(pk__in=q.values_list('pk', flat=True))

    def __str__(self):
        return str(self.persona)

    class Meta:
        verbose_name = "Reperibilità"
        verbose_name_plural = "Reperibilità"
        ordering = ["-inizio", "-fine"]
        permissions = (
            ("view_reperibilita", "Can view Reperibilità"),
        )


class TurnoSO(ModelloSemplice, ConMarcaTemporale, ConGiudizio):
    # todo: rename attivita field
    attivita = models.ForeignKey(ServizioSO, related_name='turni_so', on_delete=models.CASCADE)
    nome = models.CharField(max_length=128, default="Nuovo turno", db_index=True)
    inizio = models.DateTimeField("Data e ora di inizio", db_index=True, null=False)
    fine = models.DateTimeField("Data e ora di fine", db_index=True, null=True, blank=True, default=None)
    minimo = models.SmallIntegerField(verbose_name="Num. minimo di partecipanti", db_index=True, default=1)
    massimo = models.SmallIntegerField(verbose_name="Num. massimo di partecipanti", db_index=True, blank=True, null=True, default=None)

    PER_PAGINA = 10

    TURNO_PUOI_PARTECIPARE_PRENOTA = "P"
    TURNO_PUOI_PARTECIPARE_DISPONIBILITA = "D"
    TURNO_PUOI_PARTECIPARE = (
        TURNO_PUOI_PARTECIPARE_DISPONIBILITA,
        TURNO_PUOI_PARTECIPARE_PRENOTA
    )

    TURNO_NON_PUOI_PARTECIPARE_RISERVA = "NPPR"
    TURNO_NON_PUOI_PARTECIPARE_FUORI_SEDE = "NPPF"
    TURNO_NON_PUOI_PARTECIPARE_PASSATO = "NPPP"
    TURNO_NON_PUOI_PARTECIPARE_NEGATO = "NPNE"
    TURNO_NON_PUOI_PARTECIPARE_ACCEDI = "NPNA"
    TURNO_NON_PUOI_PARTECIPARE_ATTIVITA_CHIUSA = "NPAC"
    TURNO_NON_PUOI_PARTECIPARE_TROPPO_TARDI = "NPTT"
    TURNO_NON_PUOI_PARTECIPARE = (
        TURNO_NON_PUOI_PARTECIPARE_RISERVA,
        TURNO_NON_PUOI_PARTECIPARE_FUORI_SEDE,
        TURNO_NON_PUOI_PARTECIPARE_PASSATO,
        TURNO_NON_PUOI_PARTECIPARE_NEGATO,
        TURNO_NON_PUOI_PARTECIPARE_ACCEDI,
        TURNO_NON_PUOI_PARTECIPARE_ATTIVITA_CHIUSA,
        TURNO_NON_PUOI_PARTECIPARE_TROPPO_TARDI,
    )

    TURNO_PRENOTATO_PUOI_RITIRARTI = "PPR"
    TURNO_PRENOTATO_NON_PUOI_RITIRARTI = "TP"
    TURNO_PRENOTATO = (
        TURNO_PRENOTATO_PUOI_RITIRARTI,
        TURNO_PRENOTATO_NON_PUOI_RITIRARTI,
    )

    @property
    def url(self):
        return "%sturni/link-permanente/%d/" % (self.attivita.url, self.pk)

    @property
    def url_modifica(self):
        return "%sturni/modifica/link-permanente/%d/" % (self.attivita.url, self.pk)

    @property
    def url_cancella(self):
        return "%sturni/cancella/%d/" % (self.attivita.url, self.pk)

    @property
    def url_partecipa(self):
        return "%sturni/%d/partecipa/" % (self.attivita.url, self.pk)

    @property
    def url_ritirati(self):
        return "%sturni/%d/ritirati/" % (self.attivita.url, self.pk)

    @property
    def url_partecipanti(self):
        return "%sturni/%d/partecipanti/" % (self.attivita.url, self.pk)


    @property
    def link(self):
        return "<a href='%s'>%s</a>" % (self.url, self.nome)

    @classmethod
    @concept
    def query_futuri(cls, *args, ora=None, **kwargs):
        ora = ora or timezone.now()
        return Q(*args, fine__gt=ora, **kwargs)

    @classmethod
    @concept
    def query_passati(cls, *args, ora=None, **kwargs):
        ora = ora or timezone.now()
        return Q(*args, fine__lt=ora, **kwargs)

    def elenco_pagina(self):
        return floor(((self.elenco_posizione() - 1) / self.PER_PAGINA)) + 1

    def persona(self, persona):
        """
        Ritorna uno stato TURNO_ per la persona.
        :return:
        """
        from anagrafica.models import Appartenenza

        # Cerca la ultima richiesta di partecipazione al turno
        partecipazione = PartecipazioneSO.objects.filter(persona=persona,
                                                         turno=self).order_by('-creazione').first()

        # Se esiste una richiesta di partecipazione
        if partecipazione:

            esito = partecipazione.esito

            if esito == partecipazione.ESITO_OK:
                return self.TURNO_PRENOTATO_NON_PUOI_RITIRARTI

            elif esito == partecipazione.ESITO_PENDING:
                return self.TURNO_PRENOTATO_PUOI_RITIRARTI

            elif esito == partecipazione.ESITO_RITIRATA:
                return self.TURNO_PUOI_PARTECIPARE_PRENOTA

            else:  # esito == partecipazione.ESITO_NO
                return self.TURNO_NON_PUOI_PARTECIPARE_NEGATO

        # Altrimenti, se non esiste, controlla i requisiti di partecipazione

        ## Turno passato, puoi solo essere inserito
        if not self.futuro:
            return self.TURNO_NON_PUOI_PARTECIPARE_PASSATO

        # Attivita chiusa
        if not self.attivita.apertura == self.attivita.APERTA:
            return self.TURNO_NON_PUOI_PARTECIPARE_ATTIVITA_CHIUSA

        # Sede valida
        if not self.attivita.estensione.ottieni_discendenti(includimi=True).filter(
                pk__in=persona.sedi_attuali(membro__in=Appartenenza.MEMBRO_ATTIVITA).values_list('id', flat=True)
        ).exists():
            return self.TURNO_NON_PUOI_PARTECIPARE_FUORI_SEDE

        # In riserva
        if persona.in_riserva:
            return self.TURNO_NON_PUOI_PARTECIPARE_RISERVA

        # Se tutti i requisiti sono passati, puoi partecipare.

        ## Turno pieno? Allora dai disponibilita'.
        if self.pieno:
            return self.TURNO_PUOI_PARTECIPARE_DISPONIBILITA

        ## In tutti gli altri casi.
        return self.TURNO_PUOI_PARTECIPARE_PRENOTA

    def partecipazioni_in_attesa(self):
        return PartecipazioneSO.con_esito_pending().filter(turno=self)

    def partecipazioni_confermate(self):
        return PartecipazioneSO.con_esito_ok().filter(turno=self)

    def partecipazioni_negate(self):
        return PartecipazioneSO.con_esito_no().filter(turno=self)

    def partecipazioni_ritirate(self):
        return PartecipazioneSO.con_esito_ritirata().filter(turno=self)

    def aggiungi_partecipante(self, persona, richiedente=None):
        """
        Aggiunge di ufficio una persona.
        :return: Oggetto Partecipazione.
        """

        # Persona già partecipante?
        p = PartecipazioneSO.con_esito_ok().filter(turno=self, persona=persona).first()
        if p:
            return p

        # Elimina eventuali vecchie partecipazioni in attesa
        PartecipazioneSO.con_esito_pending().filter(turno=self, persona=persona).delete()

        p = PartecipazioneSO(turno_so=self, persona=persona,)
        p.save()

        if richiedente:
            a = Autorizzazione(
                destinatario_ruolo=INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI,
                destinatario_oggetto=self.attivita,
                oggetto=p,
                richiedente=persona,
                firmatario=richiedente,
                concessa=True,
                necessaria=False,
            )
            a.save()

        return p

    @property
    def scoperto(self):
        return self.partecipazioni_confermate().count() < self.minimo

    @property
    def pieno(self):
        return self.massimo and self.partecipazioni_confermate().count() >= self.massimo

    @property
    def futuro(self):
        return self.fine > timezone.now()

    def elenco_posizione(self):
        """
        :return: Ottiene la posizione approssimativa di questo turno in elenco (5=quinto).
        """
        return TurnoSO.objects.filter(
            attivita=self.attivita,
            inizio__lte=self.inizio,
            fine__lte=self.fine,
        ).exclude(pk=self.pk).count() + 1

    @classmethod
    def calendario_di(cls, persona, inizio, fine):
        """
        Ritorna il QuerySet per i turni da mostrare in calendario alla Persona.
        :param inizio: datetime.date per il giorno di inizio (incl.)
        :param fine: datetime.date per il giorno di fine (incl.)
        :return: QuerySet per Turno
        """
        sedi = persona.sedi_attuali(membro__in=Appartenenza.MEMBRO_ATTIVITA)

        return TurnoSO.objects.filter(
            # Attivtia organizzate dai miei comitati
            Q(attivita__sede__in=sedi)
            # Attivita aperte ai miei comitati
            | Q(attivita__estensione__in=Sede.objects.get_queryset_ancestors(
                sedi, include_self=True))
            # Attivita che gesticsco
            | Q(attivita__in=persona.oggetti_permesso(GESTIONE_SERVIZI))
            , inizio__gte=inizio, fine__lt=(fine + timedelta(1)),
            attivita__stato=ServizioSO.VISIBILE,
        ).order_by('inizio')

    class Meta:
        verbose_name = "Turno di Servizio"
        verbose_name_plural = "Turni dei Servizi"
        ordering = ['inizio', 'fine', 'id',]
        index_together = [
            ['inizio', 'fine',],
            ['attivita', 'inizio',],
            ['attivita', 'inizio', 'fine'],
        ]
        permissions = (
            ("view_turno", "Can view turno"),
        )

    def __str__(self):
        return "%s (%s)" % (self.nome, self.attivita.nome if self.attivita else "Nessuna attività")


class PartecipazioneSO(PartecipazioneAbstract):
    RICHIESTA = 'K'
    NON_PRESENTATO = 'N'
    STATO = (
        (RICHIESTA, "Part. Richiesta"),
        (NON_PRESENTATO, "Non presentato/a"),
    )

    RICHIESTA_NOME = "partecipazione attività"

    APPROVAZIONE_AUTOMATICA = timedelta(days=settings.SCADENZA_AUTORIZZAZIONE_AUTOMATICA)
    persona = models.ForeignKey("anagrafica.Persona", related_name='partecipazioni_so', on_delete=models.CASCADE)
    turno = models.ForeignKey(TurnoSO, related_name='partecipazioni_so', on_delete=models.CASCADE)
    stato = models.CharField(choices=STATO, default=RICHIESTA, max_length=1,  db_index=True)

    class Meta:
        verbose_name = "Richiesta di partecipazione al Servizio SO"
        verbose_name_plural = "Richieste di partecipazione ai Servizi SO"
        ordering = ('stato', 'persona__cognome', 'persona__nome')
        index_together = [
            ['persona', 'turno'],
            ['persona', 'turno', 'stato'],
            ['turno', 'stato'],
        ]
        permissions = (
            ("view_partecipazione", "Can view partecipazione"),
        )

    def __str__(self):
        return "%s a %s" % (self.persona.codice_fiscale, str(self.turno))


class MezzoSO(ModelloSemplice, ConMarcaTemporale, ConStorico):
    MEZZO = 'me'
    MATERIALE = 'ma'
    MEZZI_E_MATERIALI_CHOICES = (
        (MEZZO, 'Mezzo'),
        (MATERIALE, 'Materiale'),
    )

    MEZZO_CRI = 'm1'
    MEZZO_LEASING = 'm2'
    MEZZO_TIPO_CHOICES = (
        (MEZZO_CRI, 'Mezzo CRI'),
        (MEZZO_LEASING, 'Mezzo in leasing'),
    )

    tipo = models.CharField(choices=MEZZI_E_MATERIALI_CHOICES, max_length=3)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None,
                                   verbose_name='Collocazione',
                                   related_name='mezzo_materiale_estensione',
                                   on_delete=models.PROTECT)
    nome = models.CharField("Nome", max_length=255)
    mezzo_tipo = models.CharField(choices=MEZZO_TIPO_CHOICES, max_length=3, null=True, blank=True)
    creato_da = models.ForeignKey('anagrafica.Persona', null=True, blank=True)

    occupato_da = models.DateTimeField(null=True, blank=True)
    occupato_a = models.DateTimeField(null=True, blank=True)

    servizio = models.ManyToManyField(ServizioSO, blank=True)

    def __str__(self):
        return str(self.nome)

    @property
    def descrizione_mezzo(self):
        return "{}-{} {}".format(self.nome, self.estensione, 'Libero tra {} ore'.format('3') if True else False)

    class Meta:
        verbose_name = 'Mezzo o materiale'
        verbose_name_plural = 'Mezzi e materiali'
