from django.db import models

from anagrafica.models import Appartenenza, Persona, Sede
from anagrafica.permessi.incarichi import INCARICO_PRESIDENZA
from base.models import ConAutorizzazioni, ModelloSemplice
from base.tratti import ConMarcaTemporale


class BaseAutorizzazioneTest(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    richiedente = models.ForeignKey(Persona, related_name='%(app_label)s_%(class)s_autorizzazioni_test_richieste_da', on_delete=models.SET_NULL, null=True)
    persona = models.ForeignKey(Persona, related_name='%(app_label)s_%(class)s_autorizzazioni_test_persona', on_delete=models.CASCADE)
    destinazione = models.ForeignKey(Sede, related_name='%(app_label)s_%(class)s_autorizzazioni_test_destinazione', on_delete=models.PROTECT)
    appartenenza = models.ForeignKey(Appartenenza, related_name='%(app_label)s_%(class)s_autorizzazioni_test_appartenenza', null=True, blank=True, on_delete=models.CASCADE)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=512, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=4096, null=True, blank=False,)

    RICHIESTA_NOME = "AutorizzazioneTest"

    class Meta:
        abstract = True

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
            presidente = self.richiedente.sede_riferimento().presidente()
            autorizzazione = self.autorizzazioni.first()
            autorizzazione.concessa = False
            autorizzazione.firmatario = presidente
            autorizzazione.necessaria = False
            autorizzazione.save()

            self.confermata = False
            self.save()
            self.autorizzazioni.update(necessaria=False)


class ApprovaAutorizzazioneTest(BaseAutorizzazioneTest):

    _scadenza_approvazione_automatica = 30

    def autorizzazione_concessa(self, modulo=None, auto=False):
        if modulo and not auto:
            self.protocollo_data = modulo.cleaned_data['protocollo_data']
            self.protocollo_numero = modulo.cleaned_data['protocollo_numero']
            self.confermata = True
            self.save()
        elif auto and not modulo:
            presidente = self.richiedente.sede_riferimento().presidente()
            autorizzazione = self.autorizzazioni.first()
            autorizzazione.concessa = True
            autorizzazione.firmatario = presidente
            autorizzazione.necessaria = False
            autorizzazione.save()
            self.autorizzazioni.filter(progressivo=autorizzazione.progressivo).update(necessaria=False)
            if self.autorizzazioni.filter(necessaria=True).count() == 0:
                self.confermata = True
                self.save()
