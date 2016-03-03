from django.db import models

from base.models import ModelloSemplice
from base.tratti import ConStorico, ConMarcaTemporale


class Reperibilita(ModelloSemplice, ConMarcaTemporale, ConStorico):

    class Meta:
        verbose_name = "Reperibilità"
        verbose_name_plural = "Reperibilità"
        ordering = ["-inizio", "-fine"]

    attivazione = models.TimeField(verbose_name="Tempo di attivazione", help_text="Tempo necessario all'attivazione, "
                                                                                  "in formato HH:mm.", default="00:15")
    persona = models.ForeignKey("anagrafica.Persona", related_name="reperibilita", on_delete=models.CASCADE)


class Turno(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turni"
        index_together = [
            ["persona", "turno"]
        ]

    persona = models.ForeignKey("anagrafica.Persona", related_name="coturni", on_delete=models.CASCADE)
    turno = models.ForeignKey("attivita.Turno", related_name="coturni", on_delete=models.CASCADE)

    montato_da = models.ForeignKey("anagrafica.Persona", related_name="coturni_montati",
                                   null=True, default=None, on_delete=models.CASCADE)
    smontato_da = models.ForeignKey("anagrafica.Persona", related_name="coturni_smontati",
                                    null=True, default=None, on_delete=models.CASCADE)

    montato_data = models.DateTimeField(null=True)
    smontato_data = models.DateTimeField(null=True)

    @property
    def montato(self):
        return self.montato_data is not None

    @property
    def smontato(self):
        return self.montato and self.smontato_data is not None

    @property
    def montabile(self):
        return not self.montato

    @property
    def smontabile(self):
        return self.montato and not self.smontato
