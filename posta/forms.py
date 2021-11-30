from autocomplete_light import shortcuts as autocomplete_light
from django import forms
from django.core.exceptions import ValidationError

from anagrafica.models import Persona
from multiupload.fields import MultiFileField
import magic
from base.wysiwyg import WYSIWYGSemplice


MIMETYPE_TO_CHECK = ['application/csv', 'application/zip', 'application/vnd.oasis.opendocument.text',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
                    'text/plain','application/x-rar',
                    'text/rtf', 'image/tiff', 'application/pdf',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']

class ModuloScriviMessaggioSenzaDestinatari(forms.Form):

    oggetto = forms.CharField(required=True, max_length=100,)
    testo = forms.CharField(required=False, max_length=100000, widget=WYSIWYGSemplice())
    allegati = MultiFileField(min_num=0, max_num=3, max_file_size=1024*1024*10, required=False,
                              help_text="Puoi selezionare fino a 3 allegati, per un totale di 10MB.<br>I file da allegare vanno selezionati contemporaneamente, tenendo premuto CTRL.<br> Scegliendo un file alla volta, ognuno viene sovrascritto dall' altro."
                                        "<br>Tipi fi file supportati: csv, zip, rar, gif, png, jpg,  jpeg, tiff, rtf, pdf, ods, odt, doc, docx, xls, xlsx.")

    def clean(self):
        data = self.cleaned_data['allegati']
        for i in data:
            mime = magic.from_buffer(i.read(), mime=True)
            if mime not in MIMETYPE_TO_CHECK:
                raise ValidationError("Estensione <%s> di questo file non è "
                                      "accettabile." % mime)


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
