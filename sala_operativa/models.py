from datetime import timedelta, date
from math import floor, ceil

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, F, Sum, Min
from django.utils import timezone
from django.utils.timezone import now

from anagrafica.costanti import (LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, )
from anagrafica.models import Persona, Appartenenza, Sede
from anagrafica.permessi.applicazioni import REFERENTE_SERVIZI_SO
from anagrafica.permessi.costanti import GESTIONE_SERVIZI
from base.files import PDF
from base.geo import ConGeolocalizzazione
from base.models import ModelloSemplice, ConAllegati, ConAutorizzazioni
from base.tratti import ConMarcaTemporale, ConStorico, ConDelegati
from base.utils import concept, poco_fa
from posta.models import Messaggio
from social.models import ConGiudizio


class SedeInternazionaleSO(ModelloSemplice, ConMarcaTemporale):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class FunzioneSO(ModelloSemplice, ConMarcaTemporale, ConDelegati):

    COORDINAMENTO = 'COORDINAMENTO'
    OPERAZIONE_SOCCORSO_E_SANITA = 'OPERAZIONE_SOCCORSO_E_SANITA'
    OPERAZIONI_SOCIO_ASSISTENZIALI = 'OPERAZIONI_SOCIO_ASSISTENZIALI'
    PIANIFICAZIONE = 'PIANIFICAZIONE'
    LOGISTICA = 'LOGISTICA'
    AMMINISTRAZIONE_E_SEGRATERIA = 'AMMINISTRAZIONE_E_SEGRATERIA'

    SETTORE = (
        (COORDINAMENTO, 'Coordinamento'),
        (OPERAZIONE_SOCCORSO_E_SANITA, 'Operazione soccorso e sanitarie'),
        (OPERAZIONI_SOCIO_ASSISTENZIALI, 'Operazioni socio assistenziali'),
        (PIANIFICAZIONE, 'Pianificazione'),
        (LOGISTICA, 'Logistica'),
        (AMMINISTRAZIONE_E_SEGRATERIA, 'Amministrazione e segreteria'),
    )

    nome = models.CharField(max_length=100, db_index=True)
    settore = models.CharField(
        max_length=50,
        db_index=True,
        choices=SETTORE,
        default=COORDINAMENTO,
        null=True,
        blank=True
    )
    creato_da = models.ForeignKey(Persona, null=True, blank=True)

    @property
    def url_modifica(self):
        return reverse('so:funzione_modifica', args=[self.pk, ])

    @property
    def url_cancella(self):
        return reverse('so:funzione_cancella', args=[self.pk, ])

    @property
    def url_gestione(self):
        return reverse('so:gestisce_funzione')

    @property
    def url_referenti(self):
        return reverse('so:organizza_referenti_funzione', args=[self.pk, ])

    def __str__(self):
        return self.nome


class OperazioneSO(ModelloSemplice, ConMarcaTemporale, ConDelegati):

    DIPARTIMENTO_PROTEZIONE_CIVILE = 'DIPARTIMENTO_PROTEZIONE_CIVILE'
    REGIONE = 'REGIONE'
    PREFETTURA = 'PREFETTURA'
    PROVINCIA = 'PROVINCIA'
    COMUNE = 'COMUNE'
    CRI = 'CRI'
    IFRC = 'IFRC'
    ALTRO = 'ALTRO'

    ATTIVATORE = (
        (DIPARTIMENTO_PROTEZIONE_CIVILE, 'Dipartimento protezione civile'),
        (REGIONE, 'Regione'),
        (PREFETTURA, 'Prefettura'),
        (PROVINCIA, 'Provincia'),
        (COMUNE, 'Comune'),
        (CRI, 'CRI'),
        (IFRC, 'IFRC'),
        (ALTRO, 'Altro'),
    )

    NAZIONALI = 'NAZIONALI'
    INTERNAZIONALE = 'INTERNAZIONALI'

    COMITATI = (
        (NAZIONALI, 'Nazionali'),
        (INTERNAZIONALE, 'Internazionali'),
    )

    nome = models.CharField(max_length=100, db_index=True)
    # evento = #TODO: da ricevere
    impiego_bdl = models.BooleanField("L'attività prevede l'impiego dei Benefici di Legge", default=False, )
    attivatore = models.CharField(
        max_length=50,
        db_index=True,
        choices=ATTIVATORE,
        default=DIPARTIMENTO_PROTEZIONE_CIVILE,
        null=True,
        blank=True
    )
    # stato_configurazione_cri = #TODO: da ricevere
    funzioni = models.ForeignKey(FunzioneSO, on_delete=models.PROTECT, blank=True, null=True)
    inizio = models.DateTimeField(default=timezone.now, db_index=True)
    fine = models.DateTimeField(db_index=True, blank=True, null=True)
    operazione = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)
    archivia_emergenza = models.BooleanField(default=False)
    comitato = models.CharField(max_length=50, choices=COMITATI, default=NAZIONALI, blank=True, null=True)
    sede = models.ManyToManyField('anagrafica.Sede', blank=True)
    sede_internazionale = models.ManyToManyField(SedeInternazionaleSO, blank=True)

    def __str__(self):
        return self.nome

    @property
    def url(self):
        return reverse('so:operazione_info', args=[self.pk, ])

    @property
    def url_modifica(self):
        return reverse('so:operazione_modifica', args=[self.pk, ])

    @property
    def url_cancella(self):
        return reverse('so:operazione_cancella', args=[self.pk, ])

    @property
    def url_referenti(self):
        return reverse('so:organizza_referenti_operazione', args=[self.pk, ])

    @property
    def sede_allegata(self):
        return " - ".join(
            sede.nome for sede in self.sede.all()
        ) if self.sede.exists() else " - ".join(
            sede.nome for sede in self.sede_internazionale.all()
        )


class DatoreLavoro(ModelloSemplice, ConMarcaTemporale):
    nominativo = models.CharField(max_length=25, default="", db_index=True, blank=True, null=True)
    ragione_sociale = models.CharField(max_length=25, default="", db_index=True, blank=True, null=True)
    partita_iva = models.CharField(max_length=11, default="", db_index=True, blank=True, null=True)
    telefono = models.CharField(max_length=10, default="", db_index=True, blank=True, null=True)
    referente = models.CharField(max_length=25, default="", db_index=True, blank=True, null=True)
    email = models.CharField(max_length=25, default="", db_index=True, blank=True, null=True)
    pec = models.CharField(max_length=25, default="", db_index=True, blank=True, null=True)
    persona = models.ForeignKey(Persona, db_index=True, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Datore di lavoro'
        verbose_name_plural = 'Datori di lavoro'

    def __str__(self):
        return self.nominativo


class ServizioSO(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale,
                 ConGiudizio, ConAllegati, ConDelegati, ConStorico):
    BOZZA = 'B'
    VISIBILE = 'V'
    STATO = (
        (BOZZA, "Bozza"),
        (VISIBILE, "Visibile")
    )

    CHIUSA = 'C'
    APERTA = 'A'
    APERTURA = (
        (CHIUSA, 'Chiuso'),
        (APERTA, 'Aperto')
    )

    nome = models.CharField(max_length=255, default="Nuovo servizio", db_index=True)
    sede = models.ForeignKey('anagrafica.Sede', related_name='servizio', on_delete=models.PROTECT)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None,
                                   related_name='servizio_estensione', on_delete=models.PROTECT)
    stato = models.CharField(choices=STATO, default=BOZZA, max_length=1, db_index=True)
    apertura = models.CharField(choices=APERTURA, default=APERTA, max_length=1, db_index=True)
    impiego_bdl = models.BooleanField("L'attività prevede l'impiego dei Benefici di Legge", default=False, )
    descrizione = models.TextField(blank=True)
    meta = JSONField(null=True, blank=True)
    funzione = models.ForeignKey(FunzioneSO, on_delete=models.PROTECT, blank=True, null=True)

    @staticmethod
    def servizi_standard():
        choices = (
            "Coordinamento Funzione Operazioni di Soccorso e Sanitarie",
            "Coordinamento Funzione Operazioni Socio-Assistenziali",
            "Soccorso Sanitario Urgente (118)",
            "Gestione ambulatori e ambulatori mobili",
            "Servizio di Biocontenimento Sanitario",
            "Controllo Sanitario Aeroportuale",
            "Screening Temperatura Corporea in frontiera (non USMAF)",
            "Screening Temperatura Corporea non aeroportuali",
            "Supporto ai Senza Fissa Dimora",
            "Dialisi",
            "Trasporto Persone Vulnerabili",
            "Attività per i Giovani",
            "Supporto Psico-Sociale operatori",
            "Tele-supporto alla popolazione",
            "Montaggio PMA o Pre-Triage ospedalieri e relativa gestione",
            "Interviste Pre-Triage",
            "Consegna farmaci a domicilio",
            "Consegna spesa a domicilio",
            "Consegna pacchi viveri",
            "Consegna / distribuzione pasti caldi",
            "Consegna effetti personali in ospedali a pazienti COVID19+",
            "RFL – Ricongiunzione e Legami Familiari",
            "Gestione delle strutture contumaciali e hub",
        )
        return [('s_%s' % i[0], i[1]) for i in enumerate(sorted(choices), 1)]

    @property
    def url(self):
        return reverse('so:servizio', args=[self.pk, ])

    @property
    def url_cancella(self):
        return reverse('so:servizio_cancella', args=[self.pk, ])

    @property
    def url_mappa(self):
        return reverse('so:servizio_mappa', args=[self.pk, ])

    @property
    def url_turni(self):
        return reverse('so:servizio_turni', args=[self.pk, ])

    @property
    def url_modifica(self):
        return reverse('so:servizio_modifica', args=[self.pk, ])

    @property
    def url_riapri(self):
        return reverse('so:servizio_riapri', args=[self.pk, ])

    @property
    def url_partecipanti(self):
        return reverse('so:servizio_partecipanti', args=[self.pk, ])

    @property
    def url_referenti(self):
        return reverse('so:servizio_referenti', args=[self.pk, ])

    @property
    def url_richiedi_conferma(self):
        return reverse('so:servizio_richiedi_conferma', args=[self.pk, ])

    @property
    def url_conferma(self):
        return reverse('so:servizio_conferma', args=[self.pk, ])

    @property
    def url_mappa_modifica(self):
        return self.url_modifica

    @property
    def url_turni_modifica(self):
        return reverse('so:servizio_turni_modifica', args=[self.pk, ])

    @property
    def url_report(self):
        return reverse('so:servizio_report', args=[self.pk, ])

    @property
    def url_mezzi_materiali(self):
        return reverse('so:scheda_mm', args=[self.pk, ])

    @property
    def url_attestato(self):
        return reverse('so:servizio_attestati', args=[self.pk, ])

    @property
    def link(self):
        return "<a href='%s'>%s</a>" % (self.url, self.nome)

    @property
    def cancellabile(self):
        return not self.turni_so.all().exists()

    def referenti_attuali(self, al_giorno=None):
        return self.delegati_attuali(tipo=REFERENTE_SERVIZI_SO, al_giorno=al_giorno)

    def conferma_servizio(self):
        self.stato = ServizioSO.VISIBILE
        self.save()

        Messaggio.costruisci_e_accoda(
            oggetto="Attivazione corso {}".format(self.nome),
            modello="email_conferma_partecipanti.html",
            corpo={
                "nome_servizio": self.nome,
                "comitato_servizio": self.estensione,
                "link": self.url
            },
            destinatari=self.partecipanti_confermati(),
        )

        if self.estensione.estensione == LOCALE:
            referenti = self.referenti_attuali()
            presidente = self.estensione.presidente()
            if presidente not in referenti:
                referenti.append(presidente)

            Messaggio.costruisci_e_accoda(
                oggetto="Attivazione corso {}".format(self.nome),
                modello="email_conferma_referenti.html",
                corpo={
                    "nome_servizio": self.nome,
                    "comitato_servizio": self.estensione,
                    "link": self.url
                },
                destinatari=referenti,
            )

    def richiede_approvazione(self, persona):
        regionale = self.estensione.ottieni_superiori().filter(estensione=REGIONALE).first()
        presidente = regionale.presidente()

        Messaggio.costruisci_e_accoda(
            oggetto="Richiesta conferma servizio",
            modello="email_richiesta_conferma_servizio.html",
            corpo={
                "nome_servizio": self.nome,
                "comitato_servizio": self.estensione,
                "link_conferma": self.url_conferma
            },
            mittente=persona,
            destinatari=[presidente],
        )

        self.meta['richiesta_inviata'] = True
        self.save()

    @property
    def email_inviata(self):
        return True if 'richiesta_inviata' in self.meta and self.meta['richiesta_inviata'] else False

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

    def turni(self):
        return self.turni_passati() | self.turni_futuri()

    def chiudi(self, autore=None, invia_notifiche=True, azione_automatica=False):
        """
        Chiude questo servizio. Imposta il nuovo stato, sospende
        le deleghe e, se specificato, invia la notifica ai referenti.
        :param invia_notifiche: True per inviare le notifiche ai refernti di servizio, le cui
                                deleghe verranno sospese.
        :param azione_automatica: Se l'azione e' stata svolta in modo automatico (i.e. via cron) o meno.
                                  Viene usato per modificare la notifica.
        :return:
        """
        self.apertura = self.CHIUSA
        self.save()

        if invia_notifiche:
            self._invia_notifica_chiusura(autore=autore, azione_automatica=azione_automatica)

        if azione_automatica:
            self.chiusa_automaticamente = poco_fa()

        self.sospendi_deleghe()

    def riapri(self, invia_notifiche=True):
        self.apertura = self.APERTA
        self.save()
        self.attiva_deleghe()

    def ore_di_servizio(self, solo_turni_passati=True):
        """
        Calcola e ritorna il numero di ore di servizio
        :return: timedelta
        """
        turni = self.turni_passati() if solo_turni_passati else self.turni_so.all()
        turni = turni.annotate(durata=F('fine') - F('inizio'))
        a = turni.aggregate(totale_ore=Sum('durata'))
        try:
            return a['totale_ore']
        except KeyError:
            return timedelta(minutes=0)

    def eta_media_partecipanti(self):
        l = self.partecipanti_confermati().values_list('data_nascita', flat=True)
        today = date.today()
        try:
            average_age = sum((today - x for x in l), timedelta(0)) / len(l)
        except ZeroDivisionError:
            return 0
        return round(average_age.days / 365, 1)

    def partecipanti_confermati(self):
        """
        Ottiene il queryset di tutti i partecipanti confermati
        :return:
        """
        from anagrafica.models import Persona
        return Persona.objects.filter(
            pk__in=PartecipazioneSO.con_esito_ok(turno__attivita=self).
                values_list('reperibilita__persona', flat=True)
        ). \
            distinct('nome', 'cognome', 'codice_fiscale'). \
            order_by('nome', 'cognome', 'codice_fiscale')

    @property
    def attestato_scaricabile(self, me=None):
        return False if 0 in [self.turni_passati().count(),
                              self.partecipanti_confermati().count()] else True

    REPORT_FORMAT_EXCEL = 'xls'
    REPORT_FORMAT_PDF = 'pdf'

    def _genera_report(self):
        """
        Genera il report in formato PDF.
        :return:
        """
        from anagrafica.models import Persona
        turni_e_partecipanti = list()
        for turno in self.turni_passati():
            partecipanti = Persona.objects.filter(partecipazioni_so__in=turno.partecipazioni_confermate())
            turni_e_partecipanti.append((turno, partecipanti))
        return turni_e_partecipanti

    def genera_report(self, format=REPORT_FORMAT_PDF):
        corpo = {
            "attivita": self,
            "turni_e_partecipanti": self._genera_report(),
        }

        if format == self.REPORT_FORMAT_PDF:
            pdf = PDF(oggetto=self)
            pdf.genera_e_salva(
                nome="Report.pdf",
                modello="pdf_attivita_report.html",
                corpo=corpo,
                orientamento=PDF.ORIENTAMENTO_ORIZZONTALE,
            )
            return pdf

        if format == self.REPORT_FORMAT_EXCEL:
            # todo: nuovo report adeguamento
            from attivita.reports import AttivitaReport
            excel = AttivitaReport(filename='Report.xls')
            return excel.generate_and_download(data=corpo)

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
                                   help_text="Tempo necessario all'attivazione, in formato HH:mm.", )
    estensione = models.CharField(choices=ESTENSIONE_CHOICES, max_length=2)
    persona = models.ForeignKey(Persona, related_name="so_reperibilita", on_delete=models.CASCADE)
    applicazione_bdl = models.BooleanField("Applicazione dei Benefici di Legge", default=False)
    creato_da = models.ForeignKey(Persona, null=True, blank=True)
    datore_lavoro = models.ForeignKey(DatoreLavoro, blank=True, null=True)

    @classmethod
    def reperibilita_di(cls, persona):
        return cls.objects.filter(persona=persona)

    @classmethod
    def reperibilita_create_da(cls, persona):
        return cls.objects.filter(creato_da=persona)

    @classmethod
    def reperibilita_creati_da(cls, persone):
        return cls.objects.filter(creato_da__in=persone)

    @classmethod
    def reperibilita_per_sedi(cls, sedi, **kwargs):
        """

        :param sedi:
        :param kwargs:
        :return: ReperibilitaSO<QuerySet>
        """
        if isinstance(sedi, Sede):
            sedi_pks = list(sedi.esplora(includi_me=True).values_list('pk', flat=True))
            sedi = Sede.objects.filter(pk__in=sedi_pks)

        turno = kwargs.pop('turno') if 'turno' in kwargs else None
        if turno:
            q = cls.query_attuale_tra_date(inizio=turno.inizio, fine=turno.fine)
        else:
            q = cls.query_attuale_in_anno(anno=now().date().year)

        q = q.filter(
            Appartenenza.query_attuale(sede__in=sedi).via("persona__appartenenze"),
        ).order_by('attivazione', '-creazione')

        return cls.objects.filter(pk__in=q.values_list('pk', flat=True))

    @property
    def nel_turno(self):
        """
        :return: QuerySet<PartecipazioneSO>
        """
        return self.partecipazioneso_set.all()

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
    massimo = models.SmallIntegerField(verbose_name="Num. massimo di partecipanti", db_index=True, blank=True,
                                       null=True, default=None)

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
    def url_args(self):
        return self.attivita.pk, self.pk

    @property
    def url(self):
        return reverse('so:servizio_turni_link_permanente', args=self.url_args)

    @property
    def url_modifica(self):
        return reverse('so:servizio_turni_modifica_link_permanente', args=self.url_args)

    @property
    def url_cancella(self):
        return reverse('so:servizio_turni_cancella', args=self.url_args)

    @property
    def url_partecipa(self):
        return reverse('so:servizio_turni_partecipa', args=self.url_args)

    @property
    def url_ritirati(self):
        return reverse('so:servizio_turni_ritirati', args=self.url_args)

    @property
    def url_partecipanti(self):
        return reverse('so:servizio_turni_partecipanti', args=self.url_args)

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
        partecipazione = PartecipazioneSO.objects.filter(reperibilita__persona=persona,
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

    @property
    def singolo_giorno(self):
        return True if self.inizio.date() == self.fine.date() else False

    @property
    def scoperto(self):
        return self.partecipazioni_confermate().count() < self.minimo

    @property
    def pieno(self):
        return self.massimo and self.partecipazioni_confermate().count() >= self.massimo

    @property
    def futuro(self):
        return self.fine > timezone.now()

    @property
    def passato(self):
        return self.fine < timezone.now()

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

        inizio = inizio - timedelta(31)
        fine = fine + timedelta(31)

        sedi = persona.sedi_attuali(membro__in=Appartenenza.MEMBRO_SERVIZIO)
        turni = TurnoSO.objects.filter(
            # Servizi organizzati dai miei comitati
            Q(attivita__sede__in=sedi)

            # Servizi aperti ai miei comitati
            | Q(attivita__estensione__in=Sede.objects.get_queryset_ancestors(sedi, include_self=True))

            # Servizi che gesticsco
            | Q(attivita__in=persona.oggetti_permesso(GESTIONE_SERVIZI)),

            Q(inizio__range=[inizio, fine]), Q(fine__range=[inizio, fine]),

            attivita__stato=ServizioSO.VISIBILE,
        ).order_by('inizio', )
        return turni

    def aggiungi_partecipante(self, reperibilita_trovata, richiedente=None):
        return self.abbina_reperibilita(reperibilita_trovata)

    def abbina_reperibilita(self, reperibilita):
        """
        :param reperibilita:
        :return: PartecipazioneSO object
        """

        if PartecipazioneSO.objects.filter(
                reperibilita__persona=reperibilita.persona,
                reperibilita__inizio__gte=reperibilita.inizio,
                reperibilita__fine__lte=reperibilita.inizio,
                stato=PartecipazioneSO.PARTECIPA
        ).exists():
            return None, False
        else:
            partecipazione_al_turno = PartecipazioneSO(turno=self, reperibilita=reperibilita,
                                                       stato=PartecipazioneSO.PARTECIPA)
            partecipazione_al_turno.inizio = self.inizio
            partecipazione_al_turno.fine = self.fine
            partecipazione_al_turno.save()
            return partecipazione_al_turno, True

    def reperibilita_abbinate(self):
        """

        :return: PartecipazioneSO<QuerySet>
        """
        return PartecipazioneSO.reperibilita_del_turno(self)

    def trova_reperibilita(self):
        """

        :return: PartecipazioneSO<QuerySet>
        """
        servizio = self.attivita
        reperibilita = ReperibilitaSO.reperibilita_per_sedi(servizio.sede, turno=self)
        reperibilita_abbinate = self.reperibilita_abbinate().values_list('reperibilita')

        disponibili = reperibilita.exclude(pk__in=reperibilita_abbinate)
        oldest_reperibilita = disponibili.aggregate(oldest_inizio=Min('inizio'))

        # Le attività in Convenzione o non legate all’emergenza in corso non possono
        # prevedere l’attivazione dei Benefici di Legge (art. 39 e 40 del dlgs 1/2018)
        applicazione_bdl = True if self.attivita.impiego_bdl else False
        disponibili = disponibili.filter(applicazione_bdl=applicazione_bdl)

        return disponibili.exclude(
            Q(fine__lte=self.inizio),
            Q(inizio__range=[oldest_reperibilita['oldest_inizio'], self.fine])
        )

    class Meta:
        verbose_name = "Turno di Servizio"
        verbose_name_plural = "Turni dei Servizi"
        ordering = ['inizio', 'fine', 'id', ]
        index_together = [
            ['inizio', 'fine', ],
            ['attivita', 'inizio', ],
            ['attivita', 'inizio', 'fine'],
        ]
        permissions = (
            ("view_turno", "Can view turno"),
        )

    def __str__(self):
        return "%s (%s)" % (self.nome, self.attivita.nome if self.attivita else "Nessuna attività")


class PartecipazioneSO(ModelloSemplice, ConMarcaTemporale, ConStorico, ConAutorizzazioni):
    """
    Attenzione: questo modello ha ereditato dalla classe ConAutorizzazioni
    per poter utulizzare dei suoi metodi,
    ma la procedura delle autorizzazioni non fa parte delle PartecipazioneSO.
    """

    PARTECIPA = 'p'
    RITIRATO = 'r'
    STATO = (
        (PARTECIPA, "Partecipa"),
        (RITIRATO, "Ritirato"),
    )

    reperibilita = models.ForeignKey(ReperibilitaSO)
    turno = models.ForeignKey(TurnoSO, related_name='partecipazioni_so', on_delete=models.CASCADE)
    stato = models.CharField(choices=STATO, default=PARTECIPA, max_length=1, db_index=True)

    @classmethod
    def reperibilita_del_turno(cls, turno, stato=PARTECIPA):
        return cls.objects.filter(turno=turno, stato=stato)

    @classmethod
    def di_persona(cls, persona=None, **kwargs):
        if persona is None:
            return cls.objects.filter(**kwargs)
        return cls.objects.filter(reperibilita__persona=persona, **kwargs)

    @property
    def url_cancella(self):
        return reverse('so:servizio_partecipazione_cancella', args=[self.turno.pk, self.pk, ])

    @property
    def url_scarica_attestato(self):
        return reverse('so:servizio_scarica_attestato', args=[self.turno.attivita.pk, self.pk, ])

    def genera_attestato(self, request=None):
        turno = self.turno

        pdf = PDF(oggetto=self)
        pdf.genera_e_salva_con_python(
            nome="Attestato turno %s.pdf" % turno.nome,
            corpo={
                "partecipazione": self,
                "servizio": turno.attivita,
                "persona": self.reperibilita.persona,
                'request': request,
            },
            modello='pdf_attestato_turno.html',
        )
        return pdf

    class Meta:
        verbose_name = "Partecipazione al Turno di un Servizio SO"
        verbose_name_plural = "Partecipazioni ai Turni dei Servizi SO"
        index_together = [
            ['reperibilita', 'turno', ],
            ['reperibilita', 'turno', 'stato', ],
            ['turno', 'stato', ],
        ]
        permissions = (
            ("view_partecipazione", "Can view partecipazione"),
        )

    def __str__(self):
        return "%s a %s" % (self.reperibilita.persona.codice_fiscale, self.turno)


class MezzoSO(ModelloSemplice, ConMarcaTemporale):
    MEZZO = 'me'

    MATERIALE = 'ma'
    MEZZI_E_MATERIALI_CHOICES = (
        (MEZZO, 'Mezzo'),
        (MATERIALE, 'Materiale'),
    )

    MEZZO_CRI = 'm1'
    MEZZO_LEASING = 'm2'
    MEZZO_PRIVATO = 'm3'
    MEZZO_TIPO_CHOICES = (
        (MEZZO_CRI, 'Mezzo CRI'),
        (MEZZO_PRIVATO, 'Mezzo privato'),
        (MEZZO_LEASING, 'Mezzo in leasing'),
    )

    IN_SERVIZIO = 'is'
    DIMESSO = 'dm'
    FUORI_USO = 'fu'
    STATO_MM = (
        (IN_SERVIZIO, 'In servizio'),
        (DIMESSO, 'Dimesso'),
        (FUORI_USO, 'Fuori servizio')
    )

    tipo = models.CharField(choices=MEZZI_E_MATERIALI_CHOICES, max_length=3)
    mezzo_tipo = models.CharField(choices=MEZZO_TIPO_CHOICES, max_length=3,
                                  null=True, blank=True)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None,
                                   verbose_name='Collocazione',
                                   related_name='mezzo_materiale_estensione',
                                   on_delete=models.PROTECT)
    nome = models.CharField("Nome", max_length=255)
    creato_da = models.ForeignKey('anagrafica.Persona', null=True, blank=True)

    stato = models.CharField(choices=STATO_MM, max_length=2, default=IN_SERVIZIO)

    @classmethod
    def disponibili_per_sedi(cls, sedi):
        return cls.objects.filter(estensione__in=sedi)

    def abbinato_ai_servizi(self, only_actual=True):
        """
        Restituisce le prenotazioni attive.
        :return: ServizioSO<QuerySet>
        """
        fine_condition = 'fine__gt' if only_actual else 'fine__lt'
        kwargs = {
            fine_condition: now(),
        }

        prenotazioni = self.prenotazionemmso_set.filter(**kwargs)
        return ServizioSO.objects.filter(
            pk__in=prenotazioni.values_list('servizio', flat=True)
        )

    def __str__(self):
        return str(self.nome)

    class Meta:
        verbose_name = 'Mezzo o materiale'
        verbose_name_plural = 'Mezzi e materiali'


class PrenotazioneMMSO(ModelloSemplice, ConMarcaTemporale, ConStorico):
    mezzo = models.ForeignKey(MezzoSO, on_delete=models.CASCADE)
    servizio = models.ForeignKey(ServizioSO, on_delete=models.CASCADE)

    @classmethod
    def verifica_prenotabilita(cls, mezzo, inizio, fine):
        """
        :param mezzo:
        :param inizio:
        :param fine:
        :return: PrenotazioneMMSO<QuerySet>
        """

        return cls.objects.filter(
            Q(mezzo=mezzo) & (
                    Q(inizio=inizio, fine=fine)
                    | (
                            Q(inizio__lte=inizio, fine__gte=inizio)
                            | Q(inizio__lte=fine, fine__gte=fine)
                    )
            )
        )

    @classmethod
    def occupazione_nel_range(cls, mezzo, inizio, fine):
        exists = cls.verifica_prenotabilita(mezzo, inizio, fine).exists()
        return exists

    @classmethod
    def del_servizio(cls, servizio):
        return cls.objects.filter(servizio=servizio).order_by('-creazione', )

    @property
    def passata(self):
        return True if self.fine < now() else False

    class Meta:
        verbose_name = 'Prenotazione Mezzo o materiale'
        verbose_name_plural = 'Prenotazione Mezzi e materiali'
