import autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from base.wysiwyg import WYSIWYGSemplice
from formazione.models import CorsoBase, LezioneCorsoBase


class ModuloCreazioneCorsoBase(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['data_inizio', 'sede',]

    PRESSO_SEDE = "PS"
    ALTROVE = "AL"
    LOCAZIONE = (
        (PRESSO_SEDE, "Il corso si svolgerà presso la Sede."),
        (ALTROVE, "Il corso si svolgerà altrove (specifica dopo).")
    )

    locazione = forms.ChoiceField(choices=LOCAZIONE, initial=PRESSO_SEDE,
                                  help_text="La posizione del Corso è importante per "
                                            "aiutare gli aspiranti a trovare i Corsi "
                                            "che si svolgono vicino a loro.")

    def clean_sede(self):
        if self.cleaned_data['sede'].locazione is None:
            raise forms.ValidationError("La Sede CRI selezionata non ha alcun indirizzo impostato. "
                                        "Il Presidente può modificare i dettagli della Sede, tra cui l'indirizzo della stessa.")
        return self.cleaned_data['sede']


class ModuloModificaLezione(ModelForm):
    class Meta:
        model = LezioneCorsoBase
        fields = ['nome', 'inizio', 'fine']

    fine = forms.DateTimeField()

    def clean(self):
        inizio = self.cleaned_data['inizio']
        fine = self.cleaned_data['fine']
        if inizio >= fine:
            self.add_error('fine', "La fine deve essere successiva all'inizio.")


class ModuloModificaCorsoBase(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['data_inizio', 'data_esame', 'descrizione',
                  'data_attivazione', 'data_convocazione',
                  'op_attivazione', 'op_convocazione',]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }


class ModuloIscrittiCorsoBaseAggiungi(forms.Form):

    persone = autocomplete_light.ModelMultipleChoiceField("SostenitoreAutocompletamento",
                                                          help_text="Seleziona i Sostenitori CRI da iscrivere a questo"
                                                                    " Corso Base.")
