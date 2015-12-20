from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from formazione.models import CorsoBase


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