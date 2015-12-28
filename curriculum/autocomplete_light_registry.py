import autocomplete_light

from curriculum.models import Titolo


class TitoloAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['nome',]
    model = Titolo

    def choices_for_request(self):
        if 'titoli_tipo' in self.request.session:
            return self.choices.filter(inseribile_in_autonomia=True, tipo=self.request.session['titoli_tipo'])

        return self.choices.filter(inseribile_in_autonomia=True)

autocomplete_light.register(TitoloAutocompletamento)
