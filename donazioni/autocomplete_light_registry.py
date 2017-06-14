from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE
from donazioni.models import Etichetta


class EtichettaAutocompletamento(AutocompletamentoBase):
    search_fields = ('nome',)
    model = Etichetta

    def choices_for_request(self):
        me = self.request.user.persona
        sedi_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
        q = self.request.GET.get('q', '')
        self.choices = self.choices.filter(Etichetta.query_etichette_comitato(sedi_qs).q).order_by('nome')
        if q:
            self.choices = self.choices.filter(nome__icontains=q)
        return super().choices_for_request()

    choice_html_format = '''<span class="block" data-value="%s"><strong>%s</strong></span>'''

    def choice_html(self, choice):
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
        )

autocomplete_light.register(EtichettaAutocompletamento)
