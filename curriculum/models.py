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

    livello = models.ForeignKey('TitleLevel', null=True, blank=True,
                                verbose_name="Livello",
                                on_delete=models.PROTECT)
    nome = models.CharField(max_length=255, db_index=True)
    area = models.CharField(max_length=5, null=True, blank=True, db_index=True,
        choices=OBBIETTIVI_STRATEGICI)
    tipo = models.CharField(max_length=2, choices=TIPO, db_index=True)
    richiede_conferma = models.BooleanField(default=False,)
    richiede_data_ottenimento = models.BooleanField(default=False,)
    richiede_luogo_ottenimento = models.BooleanField(default=False,)
    richiede_data_scadenza = models.BooleanField(default=False,)
    richiede_codice = models.BooleanField(default=False,)
    inseribile_in_autonomia = models.BooleanField(default=True,)
    
    class Meta:
        verbose_name_plural = "Titoli: Elenco"
        permissions = (
            ("view_titolo", "Can view titolo"),
        )

    def __str__(self):
        return str(self.nome)


class TitleLevel(models.Model):
    name = models.CharField('Nome', max_length=255)
    goal = models.ForeignKey('TitleGoal', null=True, blank=True)

    @property
    def goal_obbiettivo_stragetico(self):
        return self.goal.unit_reference

    @property
    def goal_propedeuticita(self):
        return self.goal.propedeuticita

    @property
    def goal_unit_reference(self):
        return self.goal.get_unit_reference_display()

    def __str__(self):
        return "%s - %s" % (self.name, self.goal)

    class Meta:
        verbose_name = 'Titolo: Livello'
        verbose_name_plural = 'Titoli: Livelli'


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
    codice_corso = models.CharField(max_length=128, null=True,
                                    blank=True, db_index=True)
    
    certificato = models.BooleanField(default=False,)
    certificato_da = models.ForeignKey("anagrafica.Persona",
                                       null=True,
                                       related_name="titoli_da_me_certificati",
                                       on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Titolo personale"
        verbose_name_plural = "Titoli personali"
        permissions = (
            ("view_titolopersonale", "Can view titolo personale"),
        )

    @property
    def attuale(self):
        return self.data_scadenza is None or timezone.now() >= self.data_scadenza

    def autorizzazione_negata(self, modulo=None, notifiche_attive=True, data=None):
        # Alla negazione, cancella titolo personale.
        self.delete()

    def __str__(self):
        return "%s di %s" % (self.titolo, self.persona)
