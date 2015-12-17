from django import forms
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries

class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')


class ModuloMotivoNegazione(forms.Form):
    motivo = forms.CharField(label='Motivo negazione',
                             help_text="Fornisci una breve motivazione per la negazione di questa richiesta. "
                                       "Questa verrà comunicata al richiedente.",
                             required=True)


class ModuloLocalizzatore(forms.Form):
    indirizzo = forms.CharField(label='Indirizzo', required=False,)
    comune = forms.CharField()
    stato = LazyTypedChoiceField(choices=countries, initial="IT")
