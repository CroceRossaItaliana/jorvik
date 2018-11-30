from django.db.models import Q

from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Persona, Appartenenza, Sede
from curriculum.models import Titolo


class AutocompletamentoBasePersonaModelMixin(AutocompletamentoBase):
    choice_html_format = """<span class="block" data-value="%s"><strong>%s</strong> %s</span>"""

    def choice_html(self, choice):
        if choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).exists():
            app = choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        else:
            app = choice.appartenenze_attuali().first() if choice else None

        # Example: Charles Campbell (Volontario del Comitato 1 sotto Metropolitano)
        data_value = self.choice_value(choice)
        full_name = self.choice_label(choice)
        membership = ("(%s del %s)" % (app.get_membro_display(), app.sede)) if app else ''

        return self.choice_html_format % (data_value, full_name, membership)


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


class InvitaCorsoNuovoAutocompletamento(AutocompletamentoBasePersonaModelMixin):
    model = Persona
    search_fields = ['codice_fiscale',]
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


class CreateDirettoreDelegaAutocompletamento(AutocompletamentoBasePersonaModelMixin):
    model = Persona
    search_fields = ['nome', 'cognome', 'codice_fiscale',]

    def choices_for_request(self):
        self.choices = self.choices.filter(Q(Appartenenza.query_attuale(
            membro__in=Appartenenza.MEMBRO_CORSO).via("appartenenze")
        )).distinct('nome', 'cognome', 'codice_fiscale')
        return super().choices_for_request()


autocomplete_light.register(EstensioneLivelloRegionaleTitolo)
autocomplete_light.register(EstensioneLivelloRegionaleSede)
autocomplete_light.register(DocenteLezioniCorso)
autocomplete_light.register(InvitaCorsoNuovoAutocompletamento)
autocomplete_light.register(CreateDirettoreDelegaAutocompletamento)
