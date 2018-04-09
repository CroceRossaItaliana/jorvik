from django import forms
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries

from nocaptcha_recaptcha.fields import NoReCaptchaField


class ModuloResetPasswordServizio(forms.Form):
    email = forms.EmailField(label='Email')
    #captcha = NoReCaptchaField()


class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')
    captcha = NoReCaptchaField()



class ModuloMotivoNegazione(forms.Form):
    motivo = forms.CharField(label='Motivo negazione',
                             help_text="Fornisci una breve motivazione per la negazione di questa richiesta. "
                                       "Questa verrà comunicata al richiedente.",
                             required=True)


class ModuloLocalizzatore(forms.Form):
    indirizzo = forms.CharField(label='Indirizzo', required=False, help_text="es. Via Rosmini, 42. (Opzionale)")
    comune = forms.CharField(help_text="es. Cinisello Balsamo.")
    provincia = forms.CharField(required=True, min_length=3, help_text="es. Milano. (per intero)")
    stato = LazyTypedChoiceField(choices=countries, initial="IT")


class ModuloLocalizzatoreItalia(forms.Form):
    indirizzo = forms.CharField(label='Indirizzo', required=False, help_text="es. Via Rosmini, 42. (Opzionale)")
    comune = forms.CharField(help_text="es. Cinisello Balsamo.")
    provincia = forms.CharField(required=True, min_length=3, help_text="es. Milano. (per intero)")
    stato = LazyTypedChoiceField(choices=(('IT', 'Italia'),), initial="IT")
