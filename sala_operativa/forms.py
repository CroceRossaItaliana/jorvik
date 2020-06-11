from django.forms import ModelForm

from .models import ReperibilitaSO


class VolontarioReperibilitaForm(ModelForm):
    class Meta:
        model = ReperibilitaSO
        fields = ['inizio', 'fine', 'attivazione',]
