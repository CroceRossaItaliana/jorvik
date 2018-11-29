from django.db.models import Q

from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Persona, Appartenenza, Sede
from curriculum.models import Titolo


class DocenteLezioniCorso(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale',]
    model = Persona

    def choices_for_request(self):
        app_attuali = Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_CORSO)
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


class InvitaCorsoNuovoAutocompletamento(AutocompletamentoBase):
    model = Persona
    search_fields = ['codice_fiscale',]
    choice_html_format = """<span class="block" data-value="%s"><strong>%s</strong> %s</span>"""
    attrs = {
        'required': False,
        'placeholder': 'Inserisci il codice fiscale',
        'data-autocomplete-minimum-characters': 16,
    }

    def choices_for_request(self):
        self.choices = self.choices.filter(Q(Appartenenza.query_attuale(
            membro=Appartenenza.VOLONTARIO).via("appartenenze")
        ))
        return super().choices_for_request()

    def choice_html(self, choice):
        if choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).exists():
            app = choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        else:
            app = choice.appartenenze_attuali().first() if choice else None
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
            ("(%s del %s)" % (app.get_membro_display(), app.sede)) if app else '',
        )


autocomplete_light.register(EstensioneLivelloRegionaleTitolo)
autocomplete_light.register(EstensioneLivelloRegionaleSede)
autocomplete_light.register(DocenteLezioniCorso)
autocomplete_light.register(InvitaCorsoNuovoAutocompletamento)
