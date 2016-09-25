from django.core.exceptions import ValidationError
from django.db import models

from anagrafica.models import Persona
from base.models import ModelloSemplice, ConAutorizzazioni
from base.tratti import ConMarcaTemporale, ConEstensione, ConDelegati, ConStorico

__author__ = 'alfioemanuele'


def tra_1_e_6(n):
    if n < 1 or n > 6:
        raise ValidationError("Obiettivo non valido. Scegli un numero tra 1 e 6.")


class Gruppo(ModelloSemplice, ConEstensione, ConMarcaTemporale, ConDelegati):
    nome = models.CharField("Nome", max_length=255)

    obiettivo = models.IntegerField(validators=[tra_1_e_6], db_index=True)
    area = models.ForeignKey('attivita.Area', related_name='gruppi', null=True, on_delete=models.CASCADE)
    attivita = models.ForeignKey('attivita.Attivita', related_name='gruppi', null=True, on_delete=models.SET_NULL)

    def membri_attuali(self):
        return Persona.objects.filter(
            Appartenenza.query_attuale().via("appartenenze_gruppi"),
            appartenenze_gruppi__gruppo=self,
        )

    class Meta:
        verbose_name_plural = "Gruppi"
        permissions = (
            ("view_gruppo", "Can view Gruppo"),
        )

    def __str__(self):
        return "Gruppo %s" % (self.nome,)


class Appartenenza(ModelloSemplice, ConStorico, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Appartenenze"
        permissions = (
            ("view_appartenenza", "Can view Appartenenza"),
        )

    gruppo = models.ForeignKey(Gruppo, related_name='appartenenze', on_delete=models.CASCADE)
    persona = models.ForeignKey('anagrafica.Persona', related_name='appartenenze_gruppi', on_delete=models.CASCADE)

    motivo_negazione = models.CharField(max_length=512, blank=True, null=True)
    negato_da = models.ForeignKey('anagrafica.Persona', related_name='appartenenze_gruppi_negate', null=True, on_delete=models.SET_NULL)
