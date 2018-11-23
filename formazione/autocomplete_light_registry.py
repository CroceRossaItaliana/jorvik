from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Persona, Appartenenza, Sede
from curriculum.models import Titolo


class DocenteLezioniCorso(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale',]
    model = Persona

    def choices_for_request(self):
        app_attuali = Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_ATTIVITA)
        app_attuali = app_attuali.values_list('persona__id', flat=True)
        self.choices = self.choices.filter(id__in=app_attuali)
        return super().choices_for_request()


class EstensioneLivelloRegionaleTitolo(AutocompletamentoBase):
    search_fields = ['nome',]
    model = Titolo

    def choices_for_request(self):
        self.choices = self.choices.filter(tipo=Titolo.TITOLO_CRI)
        return super().choices_for_request()


class EstensioneLivelloRegionaleSede(AutocompletamentoBase):
    search_fields = ['nome',]
    model = Sede


autocomplete_light.register(EstensioneLivelloRegionaleTitolo)
autocomplete_light.register(EstensioneLivelloRegionaleSede)
autocomplete_light.register(DocenteLezioniCorso)
