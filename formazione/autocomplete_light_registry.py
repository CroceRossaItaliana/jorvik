from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Sede
from curriculum.models import Titolo


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
