from autocomplete_light import shortcuts as autocomplete_light
from django import forms

from anagrafica.models import Persona
from multiupload.fields import MultiFileField

from base.wysiwyg import WYSIWYGSemplice


class ModuloScriviMessaggioSenzaDestinatari(forms.Form):

    oggetto = forms.CharField(required=True, max_length=100,)
    testo = forms.CharField(required=False, max_length=100000, widget=WYSIWYGSemplice())
    allegati = MultiFileField(min_num=0, max_num=3, max_file_size=1024*1024*10, required=False,
                              help_text="Puoi selezionare fino a 3 allegati, per un totale di 10MB.<br>I file da allegare vanno selezionati contemporaneamente, tenendo premuto CTRL.<br> Scegliendo un file alla volta, ognuno viene sovrascritto dall' altro.")


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
