import autocomplete_light
from django import forms

from anagrafica.models import Persona
from multiupload.fields import MultiFileField


class ModuloScriviMessaggioSenzaDestinatari(forms.Form):

    oggetto = forms.CharField(required=True, max_length=100,)
    testo = forms.CharField(required=True, max_length=10000, widget=forms.Textarea)
    allegati = MultiFileField(min_num=0, max_num=3, max_file_size=1024*1024*10, required=False,
                              help_text="Puoi selezionare fino a 3 allegati, per un totale di 10MB.")


class ModuloScriviMessaggioConDestinatariVisibili(ModuloScriviMessaggioSenzaDestinatari):
    destinatari = forms.ModelMultipleChoiceField(Persona.objects.all(), widget=
                                                 autocomplete_light.MultipleChoiceWidget('PersonaAutocompletamento'))


class ModuloScriviMessaggioConDestinatariNascosti(ModuloScriviMessaggioSenzaDestinatari):
    destinatari = forms.ModelMultipleChoiceField(queryset=Persona.objects.all(), widget=forms.MultipleHiddenInput)

    destinatari_selezionati = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ModuloScriviMessaggioConDestinatariNascosti, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:  # Rende destinatari_no readonly
            self.fields['destinatari_selezionati'].widget.attrs['readonly'] = True
