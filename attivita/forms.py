from django import forms
from django.forms import ModelForm
from django.forms.extras import SelectDateWidget

from attivita.models import Attivita


class ModuloStoricoTurni(forms.Form):

    anni = (2000,)

    anno = forms.DateField(widget=SelectDateWidget(years=anni))


class ModuloAttivitaInformazioni(ModelForm):
    class Meta:
        model = Attivita
        fields = ['apertura', 'estensione', 'descrizione', 'stato', ]
