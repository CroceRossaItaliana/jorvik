from django import forms


class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')


class ModuloNegaAutorizzazione(forms.Form):
    motivo = forms.CharField(label='Motivo negazione',
                             help_text="Fornisci una breve motivazione per la negazione di questa richiesta. "
                                       "Questa verrà comunicata al richiedente.",
                             required=True)
