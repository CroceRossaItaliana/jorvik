from django.db import models

from anagrafica.models import Appartenenza, Persona, Sede
from anagrafica.permessi.incarichi import INCARICO_PRESIDENZA
from base.models import ConAutorizzazioni, ModelloSemplice
from base.tratti import ConMarcaTemporale


class BaseAutorizzazioneTest(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    richiedente = models.ForeignKey(Persona, related_name='autorizzazioni_test_richieste_da', on_delete=models.SET_NULL, null=True)
    persona = models.ForeignKey(Persona, related_name='autorizzazioni_test', on_delete=models.CASCADE)
    destinazione = models.ForeignKey(Sede, related_name='autorizzazioni_test_destinazione', on_delete=models.PROTECT)
    appartenenza = models.ForeignKey(Appartenenza, related_name='autorizzazioni_test', null=True, blank=True, on_delete=models.CASCADE)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=512, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=4096, null=True, blank=False,)

    RICHIESTA_NOME = "AutorizzazioneTest"

    def richiedi(self):
        if not self.persona.sede_riferimento():
            raise ValueError("Impossibile richiedere estensione: Nessuna appartenenza attuale.")

        self.autorizzazione_richiedi_sede_riferimento(
            self.persona,
            INCARICO_PRESIDENZA,
            invia_notifica_presidente=False
        )


class NegaAutorizzazioneTest(BaseAutorizzazioneTest):

    _scadenza_negazione_automatica = 30

    def autorizzazione_negata(self, modulo=None, auto=False):
        if modulo and not auto:
            self.protocollo_data = modulo.cleaned_data['protocollo_data']
            self.protocollo_numero = modulo.cleaned_data['protocollo_numero']
            self.confermata = False
            self.save()
        elif auto and not modulo:
            self.confermata = False
            self.save()


class ApprovaAutorizzazioneTest(BaseAutorizzazioneTest):

    _scadenza_approvazione_automatica = 30

    def autorizzazione_concessa(self, modulo=None, auto=False):
        if modulo and not auto:
            self.protocollo_data = modulo.cleaned_data['protocollo_data']
            self.protocollo_numero = modulo.cleaned_data['protocollo_numero']
            self.confermata = True
            self.ritirata = False
            self.save()
        elif auto and not modulo:
            self.confermata = True
            self.ritirata = False
            self.save()
