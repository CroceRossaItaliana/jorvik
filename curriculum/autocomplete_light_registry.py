import autocomplete_light

from curriculum.models import Titolo


class TitoloAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['nome',]
    model = Titolo

    def choices_for_request(self):
        try:
            if 'titoli_tipo' in self.request.session and 'curriculum' in self.request.META.get('HTTP_REFERER', ''):
                return self.choices.filter(inseribile_in_autonomia=True, tipo=self.request.session['titoli_tipo'])
        except:
            pass
        self.choices = self.choices.filter(inseribile_in_autonomia=True)
        return super(TitoloAutocompletamento, self).choices_for_request()

autocomplete_light.register(TitoloAutocompletamento)
