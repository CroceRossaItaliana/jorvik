import autocomplete_light
from django.forms import ModelForm

from base.wysiwyg import WYSIWYGSemplice
from donazioni.models import Campagna, Etichetta


class ModuloCampagna(ModelForm):
    class Meta:
        model = Campagna
        fields = ('inizio', 'fine', 'organizzatore', 'nome', 'descrizione',)
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }

    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento',
                                                                  help_text='Ricerca per nome fra le etichette del comitato'
                                                                            ' e quelle del Comitato Nazionale.')

    def __init__(self, *args, **kwargs):
        # instance: Campagna
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['etichette'] = kwargs['instance'].etichette.all()
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        campagna = super().save()
        campagna.etichette.clear()
        for etichetta in self.cleaned_data['etichette']:
            campagna.etichette.add(etichetta)
        etichette_correnti = campagna.etichette.all().values_list('nome', flat=True)
        if campagna.nome not in etichette_correnti:
            campagna.etichette.add(Etichetta.objects.get(nome=campagna.nome, comitato=campagna.organizzatore))

        return campagna


class ModuloEtichetta(ModelForm):
    class Meta:
        model = Etichetta
        fields = ('nome', 'comitato')
