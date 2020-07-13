from django.db.models import Q

from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Persona, Appartenenza
from anagrafica.permessi.costanti import GESTIONE_SO_SEDE


class AggiungiReperibilitaPerVolontario(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale', ]
    model = Persona

    def choices_for_request(self):
        persona = self.request.user.persona
        mie_sedi_so = persona.oggetti_permesso(GESTIONE_SO_SEDE)
        self.choices = self.choices.filter(Q(Appartenenza.query_attuale(
            membro=Appartenenza.VOLONTARIO).via("appartenenze")
        )).filter(sede__in=mie_sedi_so)
        return super().choices_for_request()


class PersonaMaterialiServizi(AutocompletamentoBase):

    search_fields = ['nome', 'cognome', 'codice_fiscale', ]
    model = Persona

    # def choices_for_request(self):
    #     persona = self.request.user.persona
    #     mie_sedi_so = persona.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    #     self.choices = self.choices.filter(Q(Appartenenza.query_attuale(
    #         membro=Appartenenza.VOLONTARIO).via("appartenenze")
    #     )).filter(sede__in=mie_sedi_so)
    #     return super().choices_for_request()


autocomplete_light.register(AggiungiReperibilitaPerVolontario)
autocomplete_light.register(PersonaMaterialiServizi)
