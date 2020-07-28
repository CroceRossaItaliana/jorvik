from django.db.models import Q

from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.autocomplete_light_registry import AutocompletamentoBase
from anagrafica.models import Persona, Appartenenza, Sede
from anagrafica.permessi.costanti import GESTIONE_SO_SEDE, GESTIONE_SERVIZI
from .models import ReperibilitaSO


class ReperibilitaGerarcichaSO(AutocompletamentoBase):
    def _clean_with_prefix(self, field):
        if self.field_prefix is not None:
            return '%s__%s' % (self.field_prefix, field)
        return field

    def cerca_reperibilita(self, sedi, field_prefix=None):
        self.field_prefix = field_prefix

        model_filter_kwargs = {
            self._clean_with_prefix('sede__in'): sedi,
        }

        return self.choices.filter(Q(Appartenenza.query_attuale(
            membro=Appartenenza.VOLONTARIO).via(self._clean_with_prefix('appartenenze'))
        )).filter(**model_filter_kwargs)\
            .order_by(self._clean_with_prefix('codice_fiscale'))\
            .distinct(self._clean_with_prefix('codice_fiscale'))


class AggiungiReperibilitaPerVolontario(ReperibilitaGerarcichaSO):
    search_fields = ['nome', 'cognome', 'codice_fiscale', ]
    model = Persona

    def choices_for_request(self):
        persona = self.request.user.persona
        mie_sedi_so = persona.oggetti_permesso(GESTIONE_SO_SEDE)

        self.choices = self.cerca_reperibilita(mie_sedi_so)
        return super().choices_for_request()


class TrovaReperibilitaPerTurno(ReperibilitaGerarcichaSO):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', ]
    model = ReperibilitaSO

    def choices_for_request(self):
        me = self.request.user.persona
        miei_servizi_GESTIONE_SERVIZI = me.oggetti_permesso(GESTIONE_SERVIZI)
        mie_sedi_GESTIONE_SO_SEDE = me.oggetti_permesso(GESTIONE_SO_SEDE)

        sedi = Sede.objects.filter(pk__in=list(miei_servizi_GESTIONE_SERVIZI.values_list('estensione', flat=True)) +
                                          list(mie_sedi_GESTIONE_SO_SEDE.values_list('pk', flat=True)))

        self.choices = self.cerca_reperibilita(sedi, 'persona')
        return super().choices_for_request()


autocomplete_light.register(TrovaReperibilitaPerTurno)
autocomplete_light.register(AggiungiReperibilitaPerVolontario)
