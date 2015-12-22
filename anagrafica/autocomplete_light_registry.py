import autocomplete_light

from anagrafica.models import Persona, Sede
from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE


class AutocompletamentoBase(autocomplete_light.AutocompleteModelBase):
    @property
    def persona(self):
        return self.request.user.persona


class PersonaAutocompletamento(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale',]
    model = Persona

    autocomplete_js_attributes = {
        'placeholder': 'Digita nome o CF...',
        'required': False,
    }

    def choices_for_request(self):
        if not self.request.user.is_staff:  #TODO udpate
            #self.choices = self.choices.filter(appartenenze__sede=self.persona.appartenenze_attuali().first().sede)
            pass
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


class SedeAutocompletamento(AutocompletamentoBase):
    search_fields = ['^nome', 'genitore__nome', ]
    model = Sede


class SedeNuovoCorsoAutocompletamento(SedeAutocompletamento):
    def choices_for_request(self):
        return self.persona.oggetti_permesso(GESTIONE_CORSI_SEDE)


autocomplete_light.register(PersonaAutocompletamento)
autocomplete_light.register(SedeAutocompletamento)
autocomplete_light.register(SedeNuovoCorsoAutocompletamento)
