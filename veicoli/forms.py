import autocomplete_light
from django import forms
from django.forms import ModelForm
from veicoli.models import Veicolo, Autoparco, Rifornimento, Manutenzione, FermoTecnico, Collocazione, Segnalazione


class ModuloCreazioneAutoparco(ModelForm):
    class Meta:
        model = Autoparco
        fields = ['nome','telefono','sede']


class ModuloCreazioneVeicolo(ModelForm):
    class Meta:
        model = Veicolo
        fields = "__all__"


class ModuloCreazioneRifornimento(autocomplete_light.ModelForm):
    class Meta:
        model = Rifornimento
        exclude = ['data', 'contachilometri', 'costo', 'consumo_carburante_lt', 'presso', 'contalitri', 'ricevuta']


class ModuloCreazioneManutenzione(autocomplete_light.ModelForm):
    class Meta:
        model = Manutenzione
        fields = ['tipo', 'data', 'descrizione', 'km', 'manutentore', 'numero_fattura', 'costo']


class ModuloCreazioneFermoTecnico(ModelForm):
    class Meta:
        model = FermoTecnico
        fields = ['motivo']


class ModuloCreazioneCollocazione(ModelForm):
    class Meta:
        model = Collocazione
        fields = ['autoparco']


class ModuloCreazioneSegnalazione(ModelForm):
    class Meta:
        model = Segnalazione
        fields = "__all__"