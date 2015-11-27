import autocomplete_light

from anagrafica.models import Persona


class PersonaAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^nome', 'cognome', 'codice_fiscale',]
    model = Persona

    def choices_for_request(self):
        if not self.request.user.is_staff:
            self.choices = self.choices.filter(private=False)

        return super(PersonaAutocompletamento, self).choices_for_request()


autocomplete_light.register(PersonaAutocompletamento)
