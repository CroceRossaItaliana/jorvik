from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Sede
from curriculum.models import Titolo


class EstensioneLivelloRegionaleTitolo(AutocompletamentoBase):
    search_fields = ['nome',]
    model = Titolo


class EstensioneLivelloRegionaleSede(AutocompletamentoBase):
    search_fields = ['nome',]
    model = Sede


autocomplete_light.register(EstensioneLivelloRegionaleTitolo)
autocomplete_light.register(EstensioneLivelloRegionaleSede)
