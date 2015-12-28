import autocomplete_light
from django import forms

from curriculum.models import TitoloPersonale, Titolo


class ModuloNuovoTitoloPersonale(autocomplete_light.ModelForm):
    class Meta:
        model = TitoloPersonale
        fields = ['titolo',]

    def __init__(self, tipo, tipo_display, *args, **kwargs):
        super(ModuloNuovoTitoloPersonale, self).__init__(*args, **kwargs)
        self.fields['titolo'].label = tipo_display
        self.fields['titolo'].queryset = Titolo.objects.filter(
            inseribile_in_autonomia=True, tipo=tipo,
        )



class ModuloDettagliTitoloPersonale(forms.ModelForm):
    class Meta:
        model = TitoloPersonale
        fields = ['data_ottenimento', 'luogo_ottenimento', 'data_scadenza', 'codice',]

    def __init__(self, *args, **kwargs):
        super(ModuloDettagliTitoloPersonale, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
