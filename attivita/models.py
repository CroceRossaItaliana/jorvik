from datetime import timedelta, date
from math import floor, ceil

from django.conf import settings
from django.db import models
from django.db.models import Q, F, Sum
from django.utils import timezone

from anagrafica.permessi.applicazioni import REFERENTE, OBIETTIVI
from anagrafica.permessi.costanti import MODIFICA
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI, INCARICO_PRESIDENZA
from base.files import PDF
from base.utils import concept, poco_fa
from posta.models import Messaggio
from social.models import ConGiudizio, ConCommenti
from base.models import ModelloSemplice, ConAutorizzazioni, ConAllegati, ConVecchioID, Autorizzazione
from base.tratti import ConMarcaTemporale, ConDelegati
from base.geo import ConGeolocalizzazione

from .reports import AttivitaReport
from .utils import valida_numero_obiettivo


class Attivita(ModelloSemplice, ConGeolocalizzazione, ConMarcaTemporale,
        ConGiudizio, ConCommenti, ConAllegati, ConDelegati, ConVecchioID):
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

    CO_AUTO = "A"
    CO_MANUALE = "M"
    CENTRALE_OPERATIVA = (
        (None, "(Disattiva)"),
        (CO_AUTO, "Automatica"),
        (CO_MANUALE, "Manuale"),
    )

    # Numero di minuti di grazie per i turni delle
    # attività di Centrale Operativa
    MINUTI_CENTRALE_OPERATIVA = 15

    # Numero di giorni che devono passare per chiudere
    #  automaticamente questa attivita' in mancanza di nuovi turni
    CHIUDI_AUTOMATICAMENTE_DOPO_GG = 60

    nome = models.CharField(max_length=255, default="Nuova attività", db_index=True, help_text="es. Aggiungi un posto a tavola")
    sede = models.ForeignKey('anagrafica.Sede', related_name='attivita', on_delete=models.PROTECT)
    area = models.ForeignKey("Area", related_name='attivita', on_delete=models.SET_NULL, null=True)
    estensione = models.ForeignKey('anagrafica.Sede', null=True, default=None, related_name='attivita_estensione', on_delete=models.PROTECT)
    stato = models.CharField(choices=STATO, default=BOZZA, max_length=1, db_index=True)
    apertura = models.CharField(choices=APERTURA, default=APERTA, max_length=1, db_index=True)
    descrizione = models.TextField(blank=True)
    centrale_operativa = models.CharField(max_length=1, default=None,
                                          blank=True, null=True,
                                          choices=CENTRALE_OPERATIVA,
                                          verbose_name="Attività di Centrale Operativa",
                                          db_index=True,
                                          help_text="Selezionando questa opzione, i partecipanti confermati verranno "
                                                    "abilitati, automaticamente o manualmente dal delegato CO, "
                                                    "all'uso del pannello di Centrale Operativa della Sede "
                                                    "da %d minuti prima dell'inizio a %d minuti dopo la fine del "
                                                    "turno." % (
                                                    MINUTI_CENTRALE_OPERATIVA,
                                                    MINUTI_CENTRALE_OPERATIVA),)

    # Questo campo viene usato per salvare un timestamp quando l'attivita e' stata chiusa automaticamente
    #  dal sistema. Dovrebbe essere controllato dal cron, in modo tale che le attivita' aperte che sono state
    #  chiuse automaticamente nel passato, non vengano chiuse automaticamente di nuovo.
    # Nota bene: Il campo non nullo non vuol dire che l'attivita' e' attualmente chiusa, semplicemente che lo e'
    #  stato in qualche momento nel passato.
    chiusa_automaticamente = models.DateTimeField(default=None, null=True, blank=True)

    @property
    def cancellabile(self):
        return not self.turni.all().exists()

    @property
    def url(self):
        return "/attivita/scheda/%d/" % self.pk

    @property
    def url_cancella(self):
        return "/attivita/scheda/%d/cancella/" % (self.pk,)

    @property
    def link(self):
        return "<a href='%s'>%s</a>" % (self.url, self.nome)

    @property
    def url_mappa(self):
        return self.url + "mappa/"

    @property
    def url_turni(self):
        return self.url + "turni/"

    @property
    def url_modifica(self):
        return self.url + "modifica/"

    @property
    def url_riapri(self):
        return self.url + "riapri/"

    @property
    def url_partecipanti(self):
        return self.url + "partecipanti/"

    @property
    def url_referenti(self):
        return self.url + "referenti/"

    @property
    def url_mappa_modifica(self):
        return self.url_modifica

    @property
    def url_turni_modifica(self):
        return self.url_turni + "modifica/"

    @property
    def url_report(self):
        return self.url + "report/"

    @property
    def url_cancella_gruppo(self):
        return "/attivita/scheda/%d/cancella-gruppo/" % (self.pk,)

    def commento_notifica_destinatari(self, mittente):
        from anagrafica.models import Persona

        # Come destinatari, sempre i delegati dell'attivita'... tranne me.
        destinatari = self.delegati_attuali().exclude(pk=mittente.pk)

        # Se posso modificare l'attività, notifica a tutti
        #  i partecipanti (sono presidente, oppure referente).
        if mittente.permessi_almeno(self, MODIFICA):
            destinatari |= Persona.objects.filter(
                partecipazioni__turno__attivita=self,
                partecipazioni__stato=Partecipazione.RICHIESTA,
                partecipazioni__turno__inizio__gte=timezone.now() - timedelta(days=120),
            )

        return destinatari.distinct()

    def referenti_attuali(self, al_giorno=None):
        return self.delegati_attuali(tipo=REFERENTE, al_giorno=al_giorno)

    def ore_uomo_di_servizio(self, solo_turni_passati=True):
        """
        Calcola e ritorna il numero di ore di servizio per uomo
        :return: timedelta
        """
        turni = self.turni_passati() if solo_turni_passati else self.turni.all()
        p = Partecipazione.con_esito_ok(turno__attivita=self).annotate(durata=F('turno__fine') - F('turno__inizio'))
        a = p.aggregate(totale_ore=Sum('durata'))
        try:
            return a['totale_ore']
        except KeyError:
            return timedelta(minutes=0)

    def pagina_turni_oggi(self):
        posizione = Turno.objects.filter(
            attivita=self,
            fine__lte=timezone.now(),
        ).count()
        return max(ceil(posizione / Turno.PER_PAGINA), 1)

    def turni_futuri(self, *args, **kwargs):
        return Turno.query_futuri(
            *args,
            attivita=self,
            **kwargs
        )

    def turni_passati(self, *args, **kwargs):
        return Turno.query_passati(
            *args,
            attivita=self,
            **kwargs
        )

    def _invia_notifica_chiusura(self, autore, azione_automatica):
        """
        Invia una e-mail di notifica ai delegati della chiusura automatica di questa attivita'.
        :param azione_automatica: Se l'azione e' stata svolta in modo automatico (i.e. via cron) o meno.
                                  Viene usato per modificare la notifica.
        """
        Messaggio.costruisci_e_accoda(oggetto="Chiusura automatica: %s" % self.nome,
                                      mittente=(None if azione_automatica else autore),
                                      destinatari=self.delegati_attuali(solo_deleghe_attive=True),
                                      modello="email_attivita_chiusa.html",
                                      corpo={"azione_automatica": azione_automatica,
                                             "autore": autore,
                                             "attivita": self})

    def chiudi(self, autore=None, invia_notifiche=True, azione_automatica=False):
        """
        Chiude questa attivita. Imposta il nuovo stato, sospende
        le deleghe e, se specificato, invia la notifica ai referenti.
        :param invia_notifiche: True per inviare le notifiche ai refernti di attivita, le cui
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
        turni = self.turni_passati() if solo_turni_passati else self.turni.all()
        turni = turni.annotate(durata=F('fine') - F('inizio'))
        a = turni.aggregate(totale_ore=Sum('durata'))
        try:
            return a['totale_ore']
        except KeyError:
            return timedelta(minutes=0)

    def eta_media_partecipanti(self):
        from anagrafica.models import Persona
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
            Partecipazione.con_esito_ok(turno__attivita=self).via("partecipazioni")
        ).distinct('nome', 'cognome', 'codice_fiscale').order_by('nome', 'cognome', 'codice_fiscale')

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
            partecipanti = Persona.objects.filter(
                partecipazioni__in=turno.partecipazioni_confermate())
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
            excel = AttivitaReport(filename='Report.xls')
            return excel.generate_and_download(data=corpo)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Attività"
        verbose_name_plural = "Attività"
        ordering = ['-creazione', 'nome',]
        index_together = [
            ['sede', 'estensione'],
            ['sede', 'estensione', 'apertura',],
            ['sede', 'estensione', 'stato',],
            ['sede', 'estensione', 'apertura', 'stato',],
            ['sede', 'apertura'],
            ['estensione', 'apertura'],
            ['centrale_operativa', 'sede'],
        ]
        permissions = (
            ("view_attivita", "Can view attivita"),
        )


class Turno(ModelloSemplice, ConMarcaTemporale, ConGiudizio):
    attivita = models.ForeignKey(Attivita, related_name='turni', on_delete=models.CASCADE)

    nome = models.CharField(max_length=128, default="Nuovo turno", db_index=True)

    inizio = models.DateTimeField("Data e ora di inizio", db_index=True, null=False)
    fine = models.DateTimeField("Data e ora di fine", db_index=True, null=True, blank=True, default=None)
    prenotazione = models.DateTimeField("Prenotazione entro", db_index=True, null=False)

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
        return "<a href='%s'>%s</a>" % (
            self.url, self.nome
        )

    @classmethod
    @concept
    def query_futuri(cls, *args, ora=None, **kwargs):
        ora = ora or timezone.now()
        return Q(
            *args,
            fine__gt=ora,
            **kwargs
        )

    @classmethod
    @concept
    def query_passati(cls, *args, ora=None, **kwargs):
        ora = ora or timezone.now()
        return Q(
            *args,
            fine__lt=ora,
            **kwargs
        )

    def elenco_pagina(self):
        return floor(((self.elenco_posizione() - 1) / self.PER_PAGINA)) + 1

    def persona(self, persona):
        """
        Ritorna uno stato TURNO_ per la persona.
        :return:
        """
        from anagrafica.models import Appartenenza

        # Cerca la ultima richiesta di partecipazione al turno
        partecipazione = Partecipazione.objects.filter(persona=persona, turno=self).order_by('-creazione').first()

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

        if self.troppo_tardi:
            return self.TURNO_NON_PUOI_PARTECIPARE_TROPPO_TARDI

        ## Attivita chiusa
        if not self.attivita.apertura == self.attivita.APERTA:
            return self.TURNO_NON_PUOI_PARTECIPARE_ATTIVITA_CHIUSA

        ## Sede valida
        if not self.attivita.estensione.ottieni_discendenti(includimi=True).filter(
                pk__in=persona.sedi_attuali(membro__in=Appartenenza.MEMBRO_ATTIVITA).values_list('id', flat=True)
        ).exists():
            return self.TURNO_NON_PUOI_PARTECIPARE_FUORI_SEDE

        ## In riserva
        if persona.in_riserva:
            return self.TURNO_NON_PUOI_PARTECIPARE_RISERVA

        # Se tutti i requisiti sono passati, puoi partecipare.

        ## Turno pieno? Allora dai disponibilita'.
        if self.pieno:
            return self.TURNO_PUOI_PARTECIPARE_DISPONIBILITA

        ## In tutti gli altri casi.
        return self.TURNO_PUOI_PARTECIPARE_PRENOTA

    def partecipazioni_in_attesa(self):
        return Partecipazione.con_esito_pending().filter(turno=self)

    def partecipazioni_confermate(self):
        return Partecipazione.con_esito_ok().filter(turno=self)

    def partecipazioni_negate(self):
        return Partecipazione.con_esito_no().filter(turno=self)

    def partecipazioni_ritirate(self):
        return Partecipazione.con_esito_ritirata().filter(turno=self)

    def aggiungi_partecipante(self, persona, richiedente=None):
        """
        Aggiunge di ufficio una persona.
        :return: Oggetto Partecipazione.
        """

        ## Persona gia' partecipante?
        p = Partecipazione.con_esito_ok().filter(turno=self, persona=persona).first()
        if p:
            return p

        ## Elimina eventuali vecchie partecipazioni in attesa
        Partecipazione.con_esito_pending().filter(turno=self, persona=persona).delete()

        p = Partecipazione(
            turno=self,
            persona=persona,
        )
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
    def pieno(self):
        return self.massimo and self.partecipazioni_confermate().count() >= self.massimo

    @property
    def futuro(self):
        return self.fine > timezone.now()

    @property
    def troppo_tardi(self):
        return self.prenotazione and timezone.now() > self.prenotazione

    @property
    def scoperto(self):
        return self.partecipazioni_confermate().count() < self.minimo

    def elenco_posizione(self):
        """
        :return: Ottiene la posizione approssimativa di questo turno in elenco (5=quinto).
        """
        return Turno.objects.filter(
            attivita=self.attivita,
            inizio__lte=self.inizio,
            fine__lte=self.fine,
        ).exclude(pk=self.pk).count() + 1

    def __str__(self):
        return "%s (%s)" % (self.nome, self.attivita.nome if self.attivita else "Nessuna attività")

    class Meta:
        verbose_name_plural = "Turni"
        ordering = ['inizio', 'fine', 'id',]
        index_together = [
            ['inizio', 'fine',],
            ['attivita', 'inizio',],
            ['attivita', 'inizio', 'fine'],
        ]
        permissions = (
            ("view_turno", "Can view turno"),
        )


class Partecipazione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):
    RICHIESTA = 'K'
    NON_PRESENTATO = 'N'
    STATO = (
        (RICHIESTA, "Part. Richiesta"),
        (NON_PRESENTATO, "Non presentato/a"),
    )

    RICHIESTA_NOME = "partecipazione attività"

    APPROVAZIONE_AUTOMATICA = timedelta(days=settings.SCADENZA_AUTORIZZAZIONE_AUTOMATICA)

    persona = models.ForeignKey("anagrafica.Persona", related_name='partecipazioni', on_delete=models.CASCADE)
    turno = models.ForeignKey(Turno, related_name='partecipazioni', on_delete=models.CASCADE)
    stato = models.CharField(choices=STATO, default=RICHIESTA, max_length=1, db_index=True)

    # Utilizzato dal modulo CO - viene impostato dal delegato CO
    centrale_operativa = models.BooleanField(default=False, db_index=True)

    @property
    def url_cancella(self):
        return "/attivita/scheda/%d/partecipazione/%d/cancella/" % (
            self.turno.attivita.pk, self.pk,
        )

    def richiedi(self, notifiche_attive=True):
        """
        Richiede autorizzazione di partecipazione all'attività.
        :return:
        """

        from anagrafica.models import Appartenenza

        self.autorizzazione_richiedi(
            self.persona,
            (
                (INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI, self.turno.attivita)
            ),

            invia_notifiche=self.turno.attivita.referenti_attuali(),
            auto=Autorizzazione.NG_AUTO,
            scadenza=self.APPROVAZIONE_AUTOMATICA,
            notifiche_attive=notifiche_attive
        )

        # Se fuori sede, chiede autorizzazione al Presidente del mio Comitato.
        if not self.turno.attivita.sede.comitato.espandi(
                includi_me=True).filter(
            pk__in=self.persona.sedi_attuali(
                membro__in=Appartenenza.MEMBRO_ATTIVITA).values_list('id', flat=True)
        ).exists():
            self.autorizzazione_richiedi(
                self.persona,
                (
                    (INCARICO_PRESIDENZA, self.persona.sede_riferimento())
                ),
                invia_notifiche=self.persona.sede_riferimento().presidente(),
                auto=Autorizzazione.NG_AUTO,
                scadenza=self.APPROVAZIONE_AUTOMATICA,
                notifiche_attive=notifiche_attive
            )

    def autorizzazione_concessa(self, modulo, auto=False, notifiche_attive=True,
                                data=None):
        """
        (Automatico)
        Invia notifica di autorizzazione concessa.
        """
        # TODO
        pass

    def autorizzazione_negata(self, modulo=None, auto=False,
                              notifiche_attive=True, data=None):
        """
        (Automatico)
        Invia notifica di autorizzazione negata.
        :param motivo: Motivazione, se presente.
        """
        # TODO
        pass

    def coturno(self):
        from centrale_operativa.models import Turno as Coturno
        if not (self.esito == self.ESITO_OK):
            return None
        return Coturno.objects.filter(persona=self.persona, turno=self.turno).first()

    class Meta:
        verbose_name = "Richiesta di partecipazione"
        verbose_name_plural = "Richieste di partecipazione"
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


class Area(ModelloSemplice, ConMarcaTemporale, ConDelegati):
    sede = models.ForeignKey('anagrafica.Sede', related_name='aree', on_delete=models.PROTECT)
    nome = models.CharField(max_length=256, db_index=True, default='Generale', blank=False)
    obiettivo = models.SmallIntegerField(null=False, blank=False, default=1, db_index=True,
                                         validators=[valida_numero_obiettivo])

    class Meta:
        verbose_name_plural = "Aree"
        ordering = ['sede', 'obiettivo', 'nome',]
        index_together = [
            ['sede', 'obiettivo'],
        ]
        permissions = (
            ("view_area", "Can view area"),
        )

    def __str__(self):
        return "%s, Ob. %d: %s" % (
            self.sede.nome_completo, self.obiettivo,
            self.nome,
        )

    @property
    def codice_obiettivo(self):
        return OBIETTIVI[self.obiettivo]


class NonSonoUnBersaglio(ModelloSemplice):
    persona = models.ForeignKey("anagrafica.Persona", related_name='nonSonoUnBersaglio', on_delete=models.CASCADE)
    centro_formazione = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Referenti non sono un bersaglio"
        permissions = (
            ("view_nonSonoUnBersaglio", "Can view non sono un bersaglio"),
        )
