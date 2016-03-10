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
        fields = ['stato', 'libretto', 'targa', 'prima_immatricolazione', 'proprietario_cognome', 'proprietario_nome', 'proprietario_indirizzo', 'pneumatici_anteriori', 'pneumatici_posteriori', 'pneumatici_alt_anteriori', 'pneumatici_alt_posteriori', 'cambio', 'lunghezza', 'larghezza', 'sbalzo', 'tara', 'marca', 'modello', 'telaio', 'massa_max', 'data_immatricolazione', 'categoria', 'destinazione', 'carrozzeria', 'omologazione', 'num_assi', 'rimorchio_frenato', 'cilindrata', 'potenza_massima', 'alimentazione', 'posti', 'regime', 'card_rifornimento', 'selettiva_radio', 'telepass']


class ModuloCreazioneRifornimento(autocomplete_light.ModelForm):
    class Meta:
        model = Rifornimento
        fields = ['data', 'contachilometri', 'costo', 'consumo_carburante', 'presso', 'contalitri', 'ricevuta']


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
        fields = ['descrizione', 'manutenzione']

class ModuloFiltraVeicoli(forms.Form):

    autoparchi = forms.ModelMultipleChoiceField(queryset=Autoparco.objects.none())
    targa = forms.CharField()