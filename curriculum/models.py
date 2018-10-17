from django.db import models
from base.models import ModelloSemplice, ConAutorizzazioni, ConVecchioID
from base.tratti import ConMarcaTemporale
from django.utils import timezone

__author__ = 'alfioemanuele'


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

    # Area a cui appartiene titolo (dati allineati al doc. elenco_corsi.xls)
    AREA_SALUTE          = '1'
    AREA_SOCIALE         = '2'
    AREA_EMERGENZE       = '3'
    AREA_PRINCIPI_VALORI = '4'
    AREA_GIOVANI         = '5'
    AREA_SVILUPPO        = '6'
    AREA_CHOICES = [
        (AREA_SALUTE, 'Salute'),
        (AREA_SOCIALE, 'Sociale'),
        (AREA_EMERGENZE, 'Emergenze'),
        (AREA_PRINCIPI_VALORI, 'Principi e valori'),
        (AREA_GIOVANI, 'Giovani'),
        (AREA_SVILUPPO, 'Sviluppo'),
    ]

    tipo = models.CharField(max_length=2, choices=TIPO, db_index=True)

    richiede_conferma = models.BooleanField(default=False,)
    richiede_data_ottenimento = models.BooleanField(default=False,)
    richiede_luogo_ottenimento = models.BooleanField(default=False,)
    richiede_data_scadenza = models.BooleanField(default=False,)
    richiede_codice = models.BooleanField(default=False,)
    inseribile_in_autonomia = models.BooleanField(default=True,)

    nome = models.CharField(max_length=255, db_index=True)
    area = models.CharField(max_length=1,
                            choices=AREA_CHOICES,
                            null=True,
                            blank=True,
                            db_index=True)
    
    class Meta:
        verbose_name_plural = "Titoli"
        permissions = (
            ("view_titolo", "Can view titolo"),
        )

    def __str__(self):
        return self.nome


class TitoloPersonale(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name = "Titolo personale"
        verbose_name_plural = "Titoli personali"
        permissions = (
            ("view_titolopersonale", "Can view titolo personale"),
        )

    RICHIESTA_NOME = 'titolo'

    titolo = models.ForeignKey(Titolo, on_delete=models.CASCADE)
    persona = models.ForeignKey("anagrafica.Persona", related_name="titoli_personali", on_delete=models.CASCADE)

    data_ottenimento = models.DateField(null=True, blank=True, help_text="Data di ottenimento del Titolo o Patente. "
                                                                         "Ove applicabile, data dell'esame.")
    luogo_ottenimento = models.CharField(null=True, blank=True, help_text="Luogo di ottenimento del Titolo o Patente. "
                                                                          "Formato es.: Roma (RM).",
                                         max_length=255)
    data_scadenza = models.DateField(null=True, blank=True, help_text="Data di scadenza del Titolo o Patente.",)
    codice = models.CharField(max_length=128, null=True, blank=True, db_index=True,
                              help_text="Codice/Numero identificativo del Titolo o Patente. "
                                        "Presente sul certificato o sulla Patente.")
    codice_corso = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    certificato = models.BooleanField(default=False,)
    certificato_da = models.ForeignKey("anagrafica.Persona", null=True, related_name="titoli_da_me_certificati", on_delete=models.SET_NULL)

    @property
    def attuale(self):
        return self.data_scadenza is None or timezone.now() >= self.data_scadenza

    def autorizzazione_negata(self, modulo=None, notifiche_attive=True, data=None):
        # Alla negazione, cancella titolo personale.
        self.delete()

    def __str__(self):
        return "%s di %s" % (
            self.titolo, self.persona,
        )
