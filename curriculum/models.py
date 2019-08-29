from datetime import date

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from .areas import OBBIETTIVI_STRATEGICI
from base.models import ModelloSemplice, ConAutorizzazioni, ConVecchioID
from base.tratti import ConMarcaTemporale


class Titolo(ModelloSemplice, ConVecchioID):
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
        (TITOLO_CRI, "Titolo CRI"),
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

    goal = models.ForeignKey('TitleGoal', null=True, blank=True,
        verbose_name="Obbiettivo", on_delete=models.PROTECT)
    nome = models.CharField(max_length=255, db_index=True)
    area = models.CharField(max_length=5, null=True, blank=True, db_index=True,
        choices=OBBIETTIVI_STRATEGICI)
    tipo = models.CharField(max_length=2, choices=TIPO, db_index=True)
    sigla = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expires_after = models.IntegerField(null=True, blank=True, verbose_name="Scadenza",
        help_text='Indicare in giorni (es: per 1 anno indicare 365)')
    scheda_lezioni = JSONField(null=True, blank=True)
    scheda_obiettivi = models.TextField('Obiettivi formativi', null=True, blank=True)
    scheda_competenze_in_uscita = models.TextField('Competenze_in_uscita', null=True, blank=True)
    cdf_livello = models.CharField(max_length=3, choices=CDF_LIVELLI,
                                   null=True, blank=True)
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
    def is_titolo_cri(self):
        return self.tipo == self.TITOLO_CRI

    @property
    def is_course_title(self):
        is_titolo_cri = self.is_titolo_cri
        has_goal = self.goal
        return is_titolo_cri and bool(has_goal) and bool(has_goal.obbiettivo_stragetico)

    @property
    def is_titolo_corso_base(self):
        return self.sigla == 'CRI'

    @property
    def expires_after_timedelta(self):
        from datetime import timedelta
        days = self.expires_after if self.expires_after else 0
        if self.is_titolo_corso_base:
            days = 10 * 365
        return timedelta(days=days)

    def __str__(self):
        # if self.tipo == self.TITOLO_CRI and self.goal:
        #     return "%s - %s - %s" % (self.nome, self.goal,
        #                              self.goal.get_unit_reference_display())
        # else:
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
        return False

    @classmethod
    def get_expired_course_titles(cls):
        now = timezone.now()
        today = date(now.year, now.month, now.day)
        return cls.objects.filter(is_course_title=True, data_scadenza=today)

    def __str__(self):
        return "%s di %s" % (self.titolo, self.persona)
