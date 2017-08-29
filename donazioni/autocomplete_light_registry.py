from autocomplete_light import shortcuts as autocomplete_light
from django.db.models import Q

from anagrafica.autocomplete_light_registry import AutocompletamentoBase, SedeAutocompletamento
from anagrafica.models import Sede
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA
from donazioni.models import Etichetta


class EtichettaAutocompletamento(AutocompletamentoBase):
    search_fields = ('slug',)
    model = Etichetta

    def choices_for_request(self):
        """
        Sono disponibili per l'autocompletamento le etichette gestite dai comitati rappresentati
        più quelle del comitato nazionale. Sono escluse le etichette create di default per le campagne
        """
        me = self.request.user.persona
        sedi_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
        q = self.request.GET.get('q', '')
        self.choices = self.choices.filter(Q(default=False) & Etichetta.query_etichette_comitato(sedi_qs).q).order_by('slug')
        if q:
            self.choices = self.choices.filter(slug__icontains=q)
        return super().choices_for_request()

    choice_html_format = '<span class="block" data-value="%s"><strong>%s</strong></span>'

    def choice_html(self, choice):
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
        )


class SedeDonazioniAutocompletamento(SedeAutocompletamento):
    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        self.choices = self.persona.oggetti_permesso(GESTIONE_CAMPAGNE)
        campagne_responsabile = self.persona.oggetti_permesso(GESTIONE_CAMPAGNA).select_related('organizzatore')
        sedi_responsabile = campagne_responsabile.order_by('organizzatore').distinct('organizzatore')
        sedi_responsabile = Sede.objects.filter(pk__in=sedi_responsabile.values_list('organizzatore', flat=True))
        self.choices |= sedi_responsabile
        if q:
            self.choices = self.choices.filter(nome__icontains=q)
        return super().choices_for_request()


autocomplete_light.register(SedeDonazioniAutocompletamento)
autocomplete_light.register(EtichettaAutocompletamento)
