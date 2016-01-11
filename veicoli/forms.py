from django import forms
from django.forms import ModelForm
from veicoli.models import Veicolo, Autoparco, Rifornimento, Manutenzione, FermoTecnico, Collocazione, Segnalazione


class ModuloCreazioneAutoparco(ModelForm):
    class Meta:
        model = Autoparco
        fields = "__all__"


class ModuloCreazioneVeicolo(ModelForm):
    class Meta:
        model = Veicolo
        fields = "__all__"


class ModuloCreazioneRifornimento(ModelForm):
    class Meta:
        model = Rifornimento
        fields = "__all__"


class ModuloCreazioneManutenzione(ModelForm):
    class Meta:
        model = Manutenzione
        fields = "__all__"


class ModuloCreazioneFermoTecnico(ModelForm):
    class Meta:
        model = FermoTecnico
        fields = "__all__"


class ModuloCreazioneCollocazione(ModelForm):
    class Meta:
        model = Collocazione
        fields = "__all__"


class ModuloCreazioneSegnalazione(ModelForm):
    class Meta:
        model = Segnalazione
        fields = "__all__"