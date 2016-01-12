import datetime

import autocomplete_light
from django import forms

from anagrafica.models import Estensione, Appartenenza
from ufficio_soci.models import Tesseramento


class ModuloCreazioneEstensione(autocomplete_light.ModelForm):
    class Meta:
        model = Estensione
        fields = ['persona', 'destinazione', ]


class ModuloElencoSoci(forms.Form):
    al_giorno = forms.DateField(help_text="La data alla quale generare l'elenco soci.",
                                required=True, initial=datetime.date.today)

    def clean_al_giorno(self):  # Non permette date passate
        al_giorno = self.cleaned_data['al_giorno']
        if al_giorno < datetime.date.today():
            raise forms.ValidationError("La data deve essere futura.")
        return al_giorno


class ModuloElencoElettorato(forms.Form):
    ELETTORATO_ATTIVO = 'A'
    ELETTORATO_PASSIVO = 'P'
    ELETTORATO = (
        (ELETTORATO_ATTIVO, "Attivo"),
        (ELETTORATO_PASSIVO, "Passivo"),
    )
    al_giorno = forms.DateField(help_text="La data delle elezioni.",
                                    required=True, initial=datetime.date.today)
    elettorato = forms.ChoiceField(choices=ELETTORATO, initial=ELETTORATO_PASSIVO)


class ModuloElencoQuote(forms.Form):
    MEMBRI_VOLONTARI = Appartenenza.VOLONTARIO
    MEMBRI_ORDINARI = Appartenenza.ORDINARIO
    MEMBRI = (
        (MEMBRI_VOLONTARI, "Soci attivi (volontari)"),
        (MEMBRI_ORDINARI, "Soci ordinari"),
    )
    membri = forms.ChoiceField(choices=MEMBRI, initial=MEMBRI_VOLONTARI)

    VERSATE = 'V'
    DA_VERSARE = 'D'
    TIPO = (
        (VERSATE, 'Elenco quote versate'),
        (DA_VERSARE, 'Elenco quote NON versate')
    )
    tipo = forms.ChoiceField(choices=TIPO, initial=DA_VERSARE)

    anno = forms.IntegerField(min_value=Tesseramento.objects.earliest('anno').anno,
                              max_value=Tesseramento.objects.latest('anno').anno,
                              initial=min(datetime.datetime.now().year,
                                          Tesseramento.objects.latest('anno').anno))
