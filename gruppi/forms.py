from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.forms import ModelForm
from django.utils.timezone import now

from gruppi.models import Gruppo
from anagrafica.costanti import ESTENSIONE


class ModuloGruppoSpecifico(forms.Form):

    def __init__(self, *args, attivita_specifica, request, **kwargs):
        super(ModuloGruppoSpecifico, self).__init__(*args, **kwargs)
        self.fields['attivita_specifica'].initial = attivita_specifica
        self.fields['attivita_specifica'].queryset = attivita_specifica
        self.request = request

    attivita_specifica = forms.ModelChoiceField(required=False, queryset=None)

    def clean(self):
        if 'specifico' in self.request:
            cleaned_data = self.cleaned_data

            # Fa il controllo sull'attività.
            attivita_specifica = cleaned_data.get('attivita_specifica')
            if not attivita_specifica:  # Non è tra quelle possibili?
                self._errors['attivita_specifica'] = self.error_class(["Seleziona un'attività."])

            # Fa il controllo sull'esistenza del gruppo per l'attività selezionata.
            try:
                Gruppo.objects.get(attivita=attivita_specifica)
                self._errors['attivita_specifica'] = self.error_class(["Esiste già un gruppo per quest'attività."])
            except Gruppo.DoesNotExist:
                pass

            return cleaned_data


class ModuloGruppoNonSpecifico(forms.Form):

    def __init__(self, *args, area_permessi, request, **kwargs):
        super(ModuloGruppoNonSpecifico, self).__init__(*args, **kwargs)
        self.fields['area'].initial = area_permessi
        self.fields['area'].queryset = area_permessi
        self.request = request

    nome = forms.CharField(required=False, min_length=8, max_length=128)
    area = forms.ModelChoiceField(required=False, queryset=None)

    def clean(self):
        if 'non_specifico' in self.request:
            cleaned_data = self.cleaned_data

            # Fa il controllo sul nome.
            nome = cleaned_data.get('nome')
            if not nome:  # Nome non inserito?
                self._errors['nome'] = self.error_class(["Scrivi un nome per il gruppo (almeno 8 caratteri)."])

            # Fa il controllo sull'area.
            area = cleaned_data.get('area')
            if not area:  # Area non inserita?
                self._errors['area'] = self.error_class(["Seleziona un'area."])

            # Fa il controllo sull'esistenza del gruppo con il nome e l'area selezionati.
            try:
                Gruppo.objects.get(nome=nome, area=area)
                self._errors['area'] = self.error_class(["Esiste già un gruppo in quest'area e con questo nome."])
                self._errors['nome'] = self.error_class(["Esiste già un gruppo in quest'area e con questo nome."])
            except Gruppo.DoesNotExist:
                pass

            return cleaned_data