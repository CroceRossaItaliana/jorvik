import autocomplete_light

from anagrafica.models import Persona, Sede


class PersonaAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale',]
    model = Persona

    autocomplete_js_attributes = {
        'placeholder': 'Digita nome o CF...',
        'required': False,
    }

    def choices_for_request(self):
        if not self.request.user.is_staff:  #TODO udpate
            self.choices = self.choices.filter(appartenenze__sede=self.request.user.persona.appartenenze_attuali().first().sede)

        return super(PersonaAutocompletamento, self).choices_for_request()

    choice_html_format = u'''
        <span class="block" data-value="%s"><strong>%s</strong> %s</span>
    '''

    def choice_html(self, choice):
        app = choice.appartenenze_attuali().first() if choice else None
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
            ("(%s a %s)" % (app.get_membro_display(), app.sede)) if app else '',
        )


class SedeAutocompletamento(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^nome', ]
    model = Sede


autocomplete_light.register(PersonaAutocompletamento)
autocomplete_light.register(SedeAutocompletamento)
