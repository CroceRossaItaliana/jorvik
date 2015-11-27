import autocomplete_light

from anagrafica.models import Persona, Sede


class PersonaAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^nome', 'cognome', 'codice_fiscale',]
    model = Persona

    def choices_for_request(self):
        if not self.request.user.is_staff:  #TODO udpate
            self.choices = self.choices.filter(appartenenze__sede=self.request.user.persona.appartenenze_attuali().first().sede)

        return super(PersonaAutocompletamento, self).choices_for_request()


class SedeAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^nome', ]
    model = Sede


autocomplete_light.register(PersonaAutocompletamento)
autocomplete_light.register(SedeAutocompletamento)
