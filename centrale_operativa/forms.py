from django.forms import ModelForm

from centrale_operativa.models import Reperibilita


class ModuloNuovaReperibilita(ModelForm):
    class Meta:
        model = Reperibilita
        fields = ['inizio', 'fine', 'attivazione']