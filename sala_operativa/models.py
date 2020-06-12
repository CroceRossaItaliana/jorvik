from django.db import models

from anagrafica.models import Persona, Appartenenza
from anagrafica.costanti import ESTENSIONE
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale, ConStorico


class ReperibilitaSO(ModelloSemplice, ConMarcaTemporale, ConStorico):
    ESTENSIONE_CHOICES = ESTENSIONE

    attivazione = models.TimeField("Tempo di attivazione", default="00:15",
        help_text="Tempo necessario all'attivazione, in formato HH:mm.",)
    persona = models.ForeignKey(Persona, related_name="so_reperibilita", on_delete=models.CASCADE)
    estensione = models.CharField(choices=ESTENSIONE_CHOICES, max_length=2)
    creato_da = models.ForeignKey(Persona, null=True, blank=True)

    @classmethod
    def reperibilita_di(cls, persona):
        return cls.objects.filter(persona=persona)

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
