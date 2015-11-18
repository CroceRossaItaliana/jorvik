from django import forms
from django.forms import ModelForm
import mptt
from anagrafica.models import Sede, Persona, Appartenenza
from autenticazione.models import Utenza

class ModuloRecuperaPassword(forms.Form):
    codice_fiscale = forms.CharField(label='Codice Fiscale', max_length=16)
    email = forms.EmailField(label='Email')
