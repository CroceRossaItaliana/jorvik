from django import forms
import mptt
from anagrafica.models import Comitato, Persona


class ModuloStepComitato(forms.Form):
    comitato = mptt.forms.TreeNodeChoiceField(queryset=Comitato.objects.all())


class ModuloStepCodiceFiscale(forms.Form):
    codice_fiscale = forms.CharField()

    # Effettua dei controlli personalizzati sui sui campi
    def clean(self):
        cleaned_data = self.cleaned_data

        # Fa il controllo di univocita' sul CF
        codice_fiscale = cleaned_data.get('codice_fiscale')
        if Persona.objects.filter(codice_fiscale=codice_fiscale).exists():  # Esiste gia'?
            self._errors['codice_fiscale'] = self.error_class(['Questo codice fiscale esiste in Gaia.'])

        return cleaned_data


class ModuloStepCredenziali(forms.Form):
    email = forms.EmailField()
    password = forms.PasswordInput()


class ModuloStepAnagrafica(forms.Form):
    nome = forms.CharField()
    cognome = forms.CharField()
    data_nascita = forms.DateField(label="Data di Nascita", )
