from django.forms import ModelForm

from autocomplete_light import shortcuts as autocomplete_light

from .models import ReperibilitaSO, ServizioSO


class VolontarioReperibilitaForm(ModelForm):
    class Meta:
        model = ReperibilitaSO
        fields = ['estensione', 'inizio', 'fine', 'attivazione',]


class AggiungiReperibilitaPerVolontarioForm(ModelForm):
    persona = autocomplete_light.ModelChoiceField("AggiungiReperibilitaPerVolontario",)

    class Meta:
        model = ReperibilitaSO
        fields = ['persona', 'estensione', 'inizio', 'fine', 'attivazione',]


class ServizioSOAggiungiForm(ModelForm):
    class Meta:
        model = ServizioSO
        fields = ['name', 'inizio', 'fine', ]
