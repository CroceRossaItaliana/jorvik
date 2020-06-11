from django.db import models

from anagrafica.models import Persona
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConStorico


class ReperibilitaSO(ModelloSemplice, ConMarcaTemporale, ConStorico):
    attivazione = models.TimeField("Tempo di attivazione", default="00:15",
        help_text="Tempo necessario all'attivazione, in formato HH:mm.",)
    persona = models.ForeignKey(Persona, related_name="so_reperibilita", on_delete=models.CASCADE)

    @classmethod
    def reperibilita_di(cls, persona):
        return cls.objects.filter(persona=persona)

    def __str__(self):
        return str(self.persona)

    class Meta:
        verbose_name = "Reperibilità"
        verbose_name_plural = "Reperibilità"
        ordering = ["-inizio", "-fine"]
        permissions = (
            ("view_reperibilita", "Can view Reperibilità"),
        )
