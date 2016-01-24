import autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.extras import SelectDateWidget

from attivita.models import Attivita, Turno
from base.wysiwyg import WYSIWYGSemplice


class ModuloStoricoTurni(forms.Form):

    anni = (2000,)

    anno = forms.DateField(widget=SelectDateWidget(years=anni))


class ModuloAttivitaInformazioni(ModelForm):
    class Meta:
        model = Attivita
        fields = ['apertura', 'estensione', 'descrizione', 'stato', ]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }


class ModuloModificaTurno(ModelForm):
    class Meta:
        model = Turno
        fields = ['nome', 'inizio', 'fine', 'minimo', 'massimo', 'prenotazione']

    def clean(self):
        fine = self.cleaned_data['fine']
        inizio = self.cleaned_data['inizio']
        minimo = self.cleaned_data['minimo']
        massimo = self.cleaned_data['massimo']
        prenotazione = self.cleaned_data['prenotazione']

        if fine <= inizio:
            self.add_error("fine", "L'orario di fine turno deve essere successivo "
                                   "all'orario di inzio.")

        if prenotazione > fine:
            self.add_error("prenotazione",  "L'orario entro il quale prenotarsi deve essere "
                                            "precedente alla fine del turno. ")

        if minimo < 0:
            self.add_error("minimo", "Inserisci un numero positivo.")

        if massimo and minimo > massimo:
            self.add_error("massimo", "Il massimo deve essere maggiore del minimo.")


class ModuloCreazioneTurno(ModuloModificaTurno):
    pass


class ModuloAggiungiPartecipanti(forms.Form):
    persone = autocomplete_light.forms.ModelMultipleChoiceField("PersonaAutocompletamento",
                                                                help_text="Seleziona uno o più persone da "
                                                                          "aggiungere come partecipanti.")
