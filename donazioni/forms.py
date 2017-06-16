import autocomplete_light
from django.forms import ModelForm, Form

from base.wysiwyg import WYSIWYGSemplice
from donazioni.models import Campagna, Etichetta


class ModuloCampagna(ModelForm):
    class Meta:
        model = Campagna
        fields = ('inizio', 'fine', 'nome', 'descrizione', 'organizzatore')

        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }

    organizzatore = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                              help_text="Ricerca per nome fra le sedi di cui si ha la delega "
                                                                        "per l'organizzazione di una campagna")
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False,
                                                                  help_text='Ricerca per nome fra le etichette del comitato'
                                                                            ' e quelle del Comitato Nazionale.')

    def __init__(self, *args, **kwargs):
        # instance: Campagna
        if kwargs.get('instance'):
            # aggiunge kwargs['initial'] per inizializzare le etichette in modifica
            initial = kwargs.setdefault('initial', {})
            initial['etichette'] = kwargs['instance'].etichette.all()
        super().__init__(*args, **kwargs)
        self.fields['inizio'].required = True
        self.fields['fine'].required = True

    def save(self, commit=True):
        campagna = super().save()  # salva campagna (e aggiunge etichetta di default)
        # rimuovi tutte le etichette (tranne quella di default)
        campagna.etichette.remove(*list(campagna.etichette.filter(default=False)))
        # aggiunge tutte le etichette proveniente dal form (tranne quella di default, se presente)
        etichette_form = [e for e in self.cleaned_data['etichette'] if not e.default]
        for etichetta in etichette_form:
            campagna.etichette.add(etichetta)
        return campagna


class ModuloEtichetta(ModelForm):
    class Meta:
        model = Etichetta
        fields = ('nome', 'comitato')

    comitato = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                         help_text="Ricerca per nome fra le sedi di cui si ha la delega "
                                                                   "per l'organizzazione di una campagna")


class ModuloFiltraCampagnePerEtichetta(Form):
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False)
