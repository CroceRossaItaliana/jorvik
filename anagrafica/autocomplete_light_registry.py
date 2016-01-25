import autocomplete_light
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from anagrafica.models import Persona, Sede, Appartenenza
from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE


class AutocompletamentoBase(autocomplete_light.AutocompleteModelBase):
    @property
    def persona(self):
        return self.request.user.persona

    empty_html_format = "<span class=\"block allinea-centro text-muted\">" \
                        "<strong><i class=\"fa fa-fw fa-search\"></i> Nessun risultato.</strong><br />" \
                        "&nbsp;Prova a cambiare il termine di ricerca.&nbsp;" \
                        "<!--%s--></span>"


class PersonaAutocompletamento(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale',]
    model = Persona

    autocomplete_js_attributes = {
        'placeholder': 'Digita nome o CF...',
        'required': False,
    }

    def choices_for_request(self):
        self.choices = self.choices.filter(
            # 1. Appartenente alla stessa mia sede
            Q(Appartenenza.query_attuale(sede__in=self.request.user.persona.sedi_attuali()).via("appartenenze"),)
            # 2. Appartenente a una sede di mia delega
            | Q(Appartenenza.query_attuale(sede__in=self.request.user.persona.sedi_deleghe_attuali()).via("appartenenze"))
        )\
            .order_by('nome', 'cognome', 'codice_fiscale')\
            .distinct('nome', 'cognome', 'codice_fiscale')
        return super(PersonaAutocompletamento, self).choices_for_request()

    choice_html_format = u'''
        <span class="block" data-value="%s"><strong>%s</strong> %s</span>
    '''

    def choice_html(self, choice):
        app = choice.appartenenze_attuali().first() if choice else None
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
            ("(%s del %s)" % (app.get_membro_display(), app.sede)) if app else '',
        )


class SedeAutocompletamento(AutocompletamentoBase):
    search_fields = ['nome', 'genitore__nome', ]
    model = Sede

    def choices_for_request(self):
        self.choices = self.choices.filter(
            attiva=True
        )
        return super(SedeAutocompletamento, self).choices_for_request()


class SedeNuovoCorsoAutocompletamento(SedeAutocompletamento):
    def choices_for_request(self):
        return self.persona.oggetti_permesso(GESTIONE_CORSI_SEDE)


autocomplete_light.register(PersonaAutocompletamento)
autocomplete_light.register(SedeAutocompletamento)
autocomplete_light.register(SedeNuovoCorsoAutocompletamento)
