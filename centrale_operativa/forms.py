from datetime import date

from django.forms import ModelForm
import django.forms as forms

from centrale_operativa.models import Reperibilita


class ModuloNuovaReperibilita(ModelForm):
    class Meta:
        model = Reperibilita
        fields = ['inizio', 'fine', 'attivazione']


class ModuloPoteri(forms.Form):
    giorno = forms.DateField(initial=date.today)
