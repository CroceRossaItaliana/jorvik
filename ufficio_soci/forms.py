import datetime

import autocomplete_light
from django import forms
from django.core.exceptions import ValidationError

from anagrafica.forms import ModuloStepAnagrafica
from anagrafica.models import Estensione, Appartenenza, Persona
from autenticazione.forms import ModuloCreazioneUtenza
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


class ModuloAggiungiPersona(ModuloStepAnagrafica):
    class Meta:
        model = Persona
        fields = ['nome', 'cognome', 'data_nascita', 'comune_nascita',
                  'provincia_nascita', 'stato_nascita', 'codice_fiscale',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza',
                  'stato_residenza', 'cap_residenza', 'email_contatto', ]


class ModuloReclamaAppartenenza(forms.ModelForm):
    class Meta:
        model = Appartenenza
        fields = ['inizio', 'sede', 'membro',]

    def __init__(self, *args, sedi, **kwargs):
        super(ModuloReclamaAppartenenza, self).__init__(*args, **kwargs)
        self.fields['sede'].choices = (
            (x.pk, x.nome_completo) for x in sedi
        )

    def clean_membro(self):
        membro = self.cleaned_data['membro']
        sede = self.cleaned_data['sede']

        if not Appartenenza.membro_permesso(sede.estensione, membro):
            raise ValidationError("La Sede selezionata non può avere questo "
                                  "tipo di membri.")

        return membro


class ModuloReclamaQuota(forms.Form):

    SI = 1
    NO = 2
    SCELTE = (
        (SI, "Sì, registra la quota per il socio"),
        (NO, "No, inserirò manualmente la quota più tardi"),
    )
    registra_quota = forms.ChoiceField(choices=SCELTE, initial=SI)

    importo_totale = forms.FloatField(initial=0)
    data_versamento = forms.DateField(initial=datetime.date.today)


class ModuloReclama(forms.Form):

    codice_fiscale = forms.CharField(min_length=9)

