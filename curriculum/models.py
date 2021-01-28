from datetime import date

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from anagrafica.permessi.incarichi import INCARICO_GESTIONE_TITOLI
from base.models import ModelloSemplice, ConAutorizzazioni, ConVecchioID
from base.tratti import ConMarcaTemporale
from posta.models import Messaggio

from .areas import OBBIETTIVI_STRATEGICI
from .validators import cv_attestato_file_upload_path


class Titolo(ModelloSemplice, ConVecchioID):
    QUALIFICHE_REGRESSO_DEADLINE = '01/06/2021'
    QUALIFICHE_REGRESSO_DEADLINE_DATE = date(year=2021, month=6, day=1)

    # Tipo del titolo
    COMPETENZA_PERSONALE = "CP"
    PATENTE_CIVILE      = "PP"
    PATENTE_CRI         = "PC"
    TITOLO_STUDIO       = "TS"
    TITOLO_CRI          = "TC"
    TIPO = (
        (COMPETENZA_PERSONALE, "Competenza Personale"),
        (PATENTE_CIVILE, "Patente Civile"),
        (PATENTE_CRI, "Patente CRI"),
        (TITOLO_STUDIO, "Titolo di Studio"),
        (TITOLO_CRI, "Qualifica CRI"),
    )

    CDF_LIVELLO_I = '1'
    CDF_LIVELLO_II = '2'
    CDF_LIVELLO_III = '3'
    CDF_LIVELLO_IV = '4'
    CDF_LIVELLI = (
        (CDF_LIVELLO_I, 'I Livello'),
        (CDF_LIVELLO_II, 'II Livello'),
        (CDF_LIVELLO_III, 'III Livello'),
        (CDF_LIVELLO_IV, 'IV Livello'),
    )

    CORSO_BASE = 'CB'
    CORSO_ONLINE = 'CO'
    CORSO_MOODLE = 'CM'
    CORSO_EQUIPOLLENZA = 'CE'
    MODALITA = (
        (CORSO_ONLINE, 'Corso online'),
        (CORSO_EQUIPOLLENZA, 'Corso equipollenza'),
    )

    goal = models.ForeignKey('TitleGoal', null=True, blank=True,
        verbose_name="Obbiettivo", on_delete=models.PROTECT)
    nome = models.CharField(max_length=255, db_index=True)
    area = models.CharField(max_length=5, null=True, blank=True, db_index=True,
        choices=OBBIETTIVI_STRATEGICI)
    tipo = models.CharField(max_length=2, choices=TIPO, db_index=True)
    modalita_titoli_cri = models.CharField(max_length=2, choices=MODALITA, db_index=True, null=True, blank=True)
    moodle = models.BooleanField(default=False, blank=True)
    sigla = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expires_after = models.IntegerField(null=True, blank=True, verbose_name="Scadenza",
        help_text='Indicare in giorni (es: per 1 anno indicare 365)')
    meta = JSONField(null=True, blank=True)
    scheda_lezioni = JSONField(null=True, blank=True)
    scheda_obiettivi = models.TextField('Obiettivi formativi', null=True, blank=True)
    scheda_competenze_in_uscita = models.TextField('Competenze_in_uscita', null=True, blank=True)
    scheda_prevede_esame = models.NullBooleanField(default=True, null=True, blank=True)
    scheda_esame_facoltativo = models.BooleanField('Esame facoltativo', default=False)
    scheda_verifica_finale = models.TextField('Tipologia di verifica finale', null=True, blank=True)
    scheda_url = models.URLField('Scheda originale', null=True, blank=True)
    cdf_livello = models.CharField(max_length=3, choices=CDF_LIVELLI, null=True, blank=True)
    cdf_durata_corso = models.CharField(max_length=255, null=True, blank=True)
    richiede_conferma = models.BooleanField(default=False)
    richiede_data_ottenimento = models.BooleanField(default=False)
    richiede_luogo_ottenimento = models.BooleanField(default=False)
    richiede_data_scadenza = models.BooleanField(default=False)
    richiede_codice = models.BooleanField(default=False)
    inseribile_in_autonomia = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Titoli: Elenco"
        permissions = (
            ("view_titolo", "Can view titolo"),
        )

    @property
    def scheda_lezioni_sorted(self):
        from collections import OrderedDict
        return OrderedDict(sorted(self.scheda_lezioni.items(), key=lambda x: int(x[0])))

    @property
    def is_titolo_cri(self):
        return self.tipo == self.TITOLO_CRI

    @property
    def is_course_title(self):
        return self.is_titolo_cri and self.sigla

    @property
    def is_titolo_corso_base(self):
        return self.sigla == 'CRI'

    @property
    def expires_after_timedelta(self):
        #
        # Aggiornato con GAIA-184: attualmente i titoli CRI non hanno una
        # scadenza, quindi questo metodo non fa niente da nessuna parte.
        #

        from datetime import timedelta
        days = self.expires_after if self.expires_after else 0
        if self.is_titolo_corso_base:
            days = 10 * 365
        return timedelta(days=days)

    @property
    def numero_partecipazioni(self):
        from formazione.models import CorsoBase

        if self.is_titolo_corso_base:
            # Corso per Volontari CRI
            return 0, 30

        if self.cdf_livello == Titolo.CDF_LIVELLO_IV:
            # Corsi di 4º livello e Alta Specializzazione
            return 0, 30000

        elif self.cdf_livello in [Titolo.CDF_LIVELLO_I, Titolo.CDF_LIVELLO_II, Titolo.CDF_LIVELLO_III]:
            # Corsi di 1º, 2º e 3º livello
            return 10, 30

        return CorsoBase.MIN_PARTECIPANTI, CorsoBase.MAX_PARTECIPANTI

    def corsi(self, **kwargs):
        return self.corsobase_set.all().filter(**kwargs)

    @staticmethod
    def gaia_323_set_values(set_to: bool):
        titoli = Titolo.objects.filter(tipo=Titolo.TITOLO_CRI,
                                       sigla__isnull=False,
                                       is_active=True,
                                       # inseribile_in_autonomia=False,
                                       area__isnull=False,
                                       nome__isnull=False,
                                       cdf_livello__isnull=False,)
        fields_to_update = {
            "inseribile_in_autonomia": str(set_to),
            "richiede_conferma": str(set_to),
        }

        print('Fields to update (%s):' % titoli.count(), fields_to_update)

        for titolo in titoli:
            if not titolo.meta:
                titolo.meta = fields_to_update
                titolo.save()
            else:
                titolo.meta.update(fields_to_update)
                titolo.save()

        print('Titotli aggiornati:', titoli)
        return titoli

    def __str__(self):
        return str(self.nome)


class TitleGoal(models.Model):
    unit_reference = models.CharField("Unità riferimento", max_length=3,
        null=True, blank=True, choices=OBBIETTIVI_STRATEGICI)
    propedeuticita = models.CharField("Propedeuticità", max_length=255,
        null=True, blank=True)

    @property
    def obbiettivo_stragetico(self):
        return self.unit_reference

    def __str__(self):
        return "%s (Obbiettivo %s)" % (self.propedeuticita, self.unit_reference)

    class Meta:
        verbose_name = 'Titolo: Propedeuticità'
        verbose_name_plural = 'Titoli: Propedeuticità'


class TitoloPersonale(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):
    RICHIESTA_NOME = 'titolo'

    ATTESTATO = 'a'
    BREVETTO = 'b'
    VERBALE_ESAME = 'v'
    ALTRO_DOC = 'd'

    TIPO_DOCUMENTAZIONE = (
        (ATTESTATO, 'Attestato'),
        (BREVETTO, 'Brevetto'),
        (VERBALE_ESAME, "Verbale d'esame"),
        (ALTRO_DOC, 'Altro documento inerente al corso'),
    )

    titolo = models.ForeignKey(Titolo, on_delete=models.CASCADE)
    persona = models.ForeignKey("anagrafica.Persona",
                                related_name="titoli_personali",
                                on_delete=models.CASCADE)

    data_ottenimento = models.DateField(null=True, blank=True,
        help_text="Data di ottenimento del Titolo o Patente. "
                  "Ove applicabile, data dell'esame.")
    luogo_ottenimento = models.CharField(max_length=255, null=True, blank=True,
        help_text="Luogo di ottenimento del Titolo o Patente. "
                  "Formato es.: Roma (RM).")
    data_scadenza = models.DateField(null=True, blank=True,
        help_text="Data di scadenza del Titolo o Patente.")
    
    codice = models.CharField(max_length=128, null=True, blank=True, db_index=True,
        help_text="Codice/Numero identificativo del Titolo o Patente. "
                    "Presente sul certificato o sulla Patente.")
    codice_corso = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    
    certificato = models.BooleanField(default=False,)
    certificato_da = models.ForeignKey("anagrafica.Persona",
                                       null=True,
                                       related_name="titoli_da_me_certificati",
                                       on_delete=models.SET_NULL)
    is_course_title = models.BooleanField(default=False)

    # GAIA-210
    tipo_documentazione = models.CharField(max_length=2, blank=True,
                                           null=True, choices=TIPO_DOCUMENTAZIONE)
    attestato_file = models.FileField(blank=True, null=True,
                             upload_to=cv_attestato_file_upload_path,
                             verbose_name='Attestato')
    direttore_corso = models.CharField(max_length=255, blank=True, null=True,
                             verbose_name='Nome del direttore del corso')
    note = models.CharField(max_length=255, blank=True, null=True)


    # ValueError: Related model u'app.model' cannot be resolved
    # https://stackoverflow.com/questions/33496333
    # curriculum.migrations.0015 was added: " ('formazione', '__first__'),"
    corso_partecipazione = models.ForeignKey('formazione.PartecipazioneCorsoBase',
                                             null=True,
                                             blank=True,
                                             on_delete=models.SET_NULL,
                                             related_name='titolo_ottenuto')

    class Meta:
        verbose_name = "Titolo personale"
        verbose_name_plural = "Titoli personali"
        permissions = (
            ("view_titolopersonale", "Can view titolo personale"),
        )

    @property
    def attuale(self):
        now = timezone.now()
        today = date(now.year, now.month, now.day)
        return self.data_scadenza is None or \
               today >= self.data_scadenza

    def autorizzazione_negata(self, modulo=None, notifiche_attive=True, data=None):
        # Alla negazione, cancella titolo personale.
        self.delete()

    @property
    def is_expired_course_title(self):
        """
        now = timezone.now()
        today = date(now.year, now.month, now.day)
        if self.titolo.is_titolo_corso_base:
            return False
        elif self.is_course_title and today > self.data_scadenza:
            return True
        return False
        """
        return False  # OBS: GAIA-184

    @classmethod
    def get_expired_course_titles(cls):
        now = timezone.now()
        today = date(now.year, now.month, now.day)
        return cls.objects.filter(is_course_title=True, data_scadenza=today)

    @property
    def qualifica_regresso(self):
        if self.tipo_documentazione and self.attestato_file:
            return True
        return False

    @property
    def can_delete(self):
        """ GAIA-207 """
        if self.confermata and self.qualifica_regresso:
            return False
        elif self.titolo.is_course_title and not self.titolo.inseribile_in_autonomia:
            return False
        return True

    def richiedi_autorizzazione(self, qualifica_nuova, me, sede_attuale):
        qualifica_nuova.autorizzazione_richiedi_sede_riferimento(me, INCARICO_GESTIONE_TITOLI)

        vo_nome_cognome = "%s %s" % (me.nome, me.cognome)
        Messaggio.costruisci_e_accoda(
            oggetto="Inserimento su GAIA Qualifiche CRI: Volontario %s" % vo_nome_cognome,
            modello="email_cv_qualifica_regressa_inserimento_mail_al_presidente.html",
            corpo={
                "volontario": me,
            },
            mittente=None,
            destinatari=[
                sede_attuale.presidente(),
            ]
        )

    @classmethod
    def crea_qualifica_regressa(cls, persona, **kwargs):
        qualifica_nuova = TitoloPersonale(persona=persona, confermata=False, **kwargs)
        qualifica_nuova.save()

        titolo = kwargs['titolo']

        if titolo.meta and titolo.meta.get('richiede_conferma'):
            sede_attuale = persona.sede_riferimento()
            if not sede_attuale:
                qualifica_nuova.delete()
                return None

            # Richiedi autorizzazione, manda le mail
            qualifica_nuova.richiedi_autorizzazione(qualifica_nuova, persona, sede_attuale)
        return qualifica_nuova

    @property
    def associated_to_a_course(self):
        return True if self.corso_partecipazione else False

    def __str__(self):
        return "%s di %s" % (self.titolo, self.persona)
