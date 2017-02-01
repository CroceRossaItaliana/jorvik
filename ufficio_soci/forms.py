import datetime

from autocomplete_light import shortcuts as autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.forms import ModelForm

from anagrafica.forms import ModuloStepAnagrafica
from anagrafica.models import Estensione, Appartenenza, Persona, Dimissione, Riserva, Trasferimento
from anagrafica.validators import valida_almeno_14_anni
from base.utils import rimuovi_scelte
from ufficio_soci.validators import valida_data_non_nel_futuro
from ufficio_soci.models import Tesseramento, Quota, Tesserino


class ModuloCreazioneEstensione(autocomplete_light.ModelForm):
    class Meta:
        model = Estensione
        fields = ['persona', 'destinazione', 'motivo']


class ModuloCreazioneTrasferimento(autocomplete_light.ModelForm):
    class Meta:
        model = Trasferimento
        fields = ['persona', 'destinazione', 'motivo']


class ModuloElencoSoci(forms.Form):
    al_giorno = forms.DateField(help_text="La data alla quale generare l'elenco soci.",
                                required=True, initial=datetime.date.today)


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


class ModuloElencoEstesi(forms.Form):
    ESTESI_INGRESSO = "I"
    ESTESI_USCITA = "U"
    ESTESI = (
        (ESTESI_INGRESSO, "Estensioni in ingresso (ex. volontari estesi)"),
        (ESTESI_USCITA, "Estensioni in uscita (ex. volontari in estensione)")
    )
    estesi = forms.ChoiceField(choices=ESTESI, initial=ESTESI_INGRESSO)


class ModuloElencoPerTitoli(forms.Form):
    METODO_OR = "OR"
    METODO_AND = "AND"
    METODI = (
        (METODO_OR, "Tutti i soci aventi ALMENO UNO dei titoli selezionati"),
        (METODO_AND, "Tutti i soci aventi TUTTI i titoli selezionati"),
    )
    metodo = forms.ChoiceField(choices=METODI, initial=METODO_OR)

    titoli = autocomplete_light.ModelMultipleChoiceField("TitoloAutocompletamento", help_text="Seleziona uno o più titoli per"
                                                                                              " la tua ricerca.")

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
    anno = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ModuloElencoQuote, self).__init__(*args, **kwargs)
        try:
            self.fields['anno'].min_value = Tesseramento.objects.earliest('anno').anno
            self.fields['anno'].max_value = Tesseramento.objects.latest('anno').anno
            self.fields['anno'].initial = min(datetime.datetime.now().year, Tesseramento.objects.latest('anno').anno if Tesseramento.objects.all().exists() else 9999)
        except Tesseramento.DoesNotExist:
            pass


class ModuloAggiungiPersona(ModuloStepAnagrafica):
    class Meta:
        model = Persona
        fields = ['nome', 'cognome', 'data_nascita', 'comune_nascita',
                  'provincia_nascita', 'stato_nascita', 'codice_fiscale',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza',
                  'stato_residenza', 'cap_residenza', 'email_contatto', ]

    def clean_data_nascita(self):
        # Permette tutte le date di nascita.
        return self.cleaned_data.get('data_nascita')


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


class ModuloCreazioneRiserva(autocomplete_light.ModelForm):
    class Meta:
        model = Riserva
        fields = ['persona', 'inizio','fine', 'motivo']

    def clean_fine(self):
        fine = self.cleaned_data['fine']
        inizio = self.cleaned_data['inizio']
        if not fine or fine < inizio:
            raise forms.ValidationError("La fine di una riserva non può avvenire prima del suo inizio")
        return fine


class ModuloReclamaQuota(forms.Form):

    SI = "S"
    NO = "N"
    SCELTE = (
    #    (SI, "Sì, registra la quota per il socio"),
        (NO, "No, inserirò manualmente la quota più tardi"),
    )
    registra_quota = forms.ChoiceField(choices=SCELTE, initial=SI)

    importo_totale = forms.FloatField(initial=0)
    data_versamento = forms.DateField(initial=datetime.date.today)


class ModuloReclama(forms.Form):

    codice_fiscale = forms.CharField(min_length=9)


class ModuloVerificaTesserino(forms.Form):

    numero_tessera = forms.CharField(max_length=13, help_text="Come riportato sul retro della tessera, "
                                                              "sotto al codice a barre.")

    def clean_numero_tessera(self):
        numero_tessera = self.cleaned_data['numero_tessera']

        if len(numero_tessera) != 13:
            raise ValidationError("Il numero della tessera è composto da 13 cifre.")

        if "8016" not in numero_tessera:
            raise ValidationError("I numeri di tessera iniziano con 8016.")

        return numero_tessera


class ModuloCreazioneDimissioni(ModelForm):
    class Meta:
        model = Dimissione
        fields = ['motivo', 'info', ]

    trasforma_in_sostenitore = forms.BooleanField(help_text="In caso di Dimissioni Volontarie seleziona quest'opzione "
                                                            "per trasformare il volontario in sostenitore. ", required=False)

    def clean_trasforma_in_sostenitore(self):
        trasforma_in_sostenitore = self.cleaned_data['trasforma_in_sostenitore']
        motivo = self.cleaned_data['motivo']
        if trasforma_in_sostenitore and motivo != Dimissione.VOLONTARIE:
            raise ValidationError("Puoi richiedere la trasformazione in sostenitore solo in "
                                  "caso di dimissioni volontarie.")
        return trasforma_in_sostenitore


class ModuloElencoRicevute(forms.Form):

    tipi_ricevute = forms.MultipleChoiceField(choices=Quota.TIPO, initial=[x[0] for x in Quota.TIPO])
    anno = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ModuloElencoRicevute, self).__init__(*args, **kwargs)
        self.fields['anno'].choices = Tesseramento.anni_scelta()
        self.fields['anno'].initial = Tesseramento.ultimo_anno()


class ModuloElencoVolontari(forms.Form):

    SI = "SI"
    NO = "NO"
    SCELTE = (
        (SI, "Sì, includi volontari estesi (in ingresso) presso le mie Sedi"),
        (NO, "No, non includere i volontari estesi (in ingresso) presso le mie Sedi"),
    )
    includi_estesi = forms.ChoiceField(choices=SCELTE, initial=SI)


class ModuloElencoIVCM(forms.Form):

    IV = "IV"
    CM = "CM"
    SCELTE = (
        (IV, "IV"),
        (CM, "CM"),
    )
    includi = forms.ChoiceField(choices=SCELTE)


class ModuloQuotaVolontario(forms.Form):
    volontario = autocomplete_light.ModelChoiceField("PersonaAutocompletamento",
                                                     help_text="Seleziona il Volontario per il quale registrare"
                                                               " la quota associativa.")
    tipo_quota = forms.ChoiceField(label='Tipo', choices=Quota.TIPI_REGISTRAZIONE_QUOTE, widget=forms.RadioSelect, required=False)
    importo = forms.FloatField(help_text="Il totale versato in euro, comprensivo dell'eventuale "
                                         "donazione aggiuntiva.")
    data_versamento = forms.DateField(validators=[valida_data_non_nel_futuro])

    def __init__(self, *args, **kwargs):
        super(ModuloQuotaVolontario, self).__init__(*args, **kwargs)
        self.fields['importo'].widget.attrs['min'] = self.initial.get('importo', 0)


class ModuloNuovaRicevuta(forms.Form):

    TIPI = (
        (Quota.QUOTA_SOSTENITORE, "Ricevuta Sostenitore CRI"),
        (Quota.RICEVUTA, "Ricevuta Semplice"),
    )
    tipo_ricevuta = forms.ChoiceField(choices=TIPI, initial=Quota.QUOTA_SOSTENITORE)

    persona = autocomplete_light.ModelChoiceField("PersonaAutocompletamento",
                                                  help_text="Seleziona la persona per la quale registrare"
                                                            " la ricevuta.")

    causale = forms.CharField(min_length=8, max_length=128)
    importo = forms.FloatField(min_value=0.01, help_text="Il totale versato in euro.")

    data_versamento = forms.DateField(validators=[valida_data_non_nel_futuro])


class ModuloFiltraEmissioneTesserini(forms.Form):

    stato_richiesta = forms.MultipleChoiceField(choices=Tesserino.STATO_RICHIESTA)
    tipo_richiesta = forms.MultipleChoiceField(choices=Tesserino.TIPO_RICHIESTA, initial=(Tesserino.RILASCIO,
                                                                                          Tesserino.RINNOVO,
                                                                                          Tesserino.DUPLICATO))
    stato_emissione = forms.MultipleChoiceField(choices=Tesserino.STATO_EMISSIONE, initial=(("", Tesserino.STAMPATO,
                                                                                             Tesserino.SPEDITO_CASA,
                                                                                             Tesserino.SPEDITO_SEDE)),)

    DATA_RICHIESTA_DESC = '-creazione'
    DATA_RICHIESTA_ASC = 'creazione'
    DATA_CONFERMA_DESC = '-data_conferma'
    DATA_CONFERMA_ASC = 'data_conferma'
    ORDINE = (
        (DATA_RICHIESTA_DESC, "Data di Richiesta (Decrescente)"),
        (DATA_RICHIESTA_ASC, "Data di Richiesta (Crescente)"),
        (DATA_CONFERMA_DESC, "Data di Conferma (Decrescente)"),
        (DATA_CONFERMA_ASC, "Data di Conferma (Crescente)"),
    )
    ordine = forms.ChoiceField(choices=ORDINE, initial=DATA_RICHIESTA_DESC)

    cerca = forms.CharField(initial="", required=False, help_text="(Opzionale) Parte del Codice Fiscale o "
                                                                  " codice tesserino.")


class ModuloLavoraTesserini(forms.Form):

    MINIMO_CARATTERI_MOTIVO_RIFIUTATO = 16

    stato_richiesta = forms.ChoiceField(choices=rimuovi_scelte([Tesserino.RICHIESTO], Tesserino.STATO_RICHIESTA),
                                        help_text="Scegli se accettare o negare la richiesta "
                                                  "di emissione dei tesserini.")
    stato_emissione = forms.ChoiceField(choices=Tesserino.STATO_EMISSIONE, required=False,
                                        help_text="Scegli se registrare i tesserini come emessi. "
                                                  "I tesserini verranno attivati una volta emessi. ")
    motivo_rifiutato = forms.CharField(help_text="Se hai negato le richieste, inserisci qui la motivazione. "
                                                 "Es.: Fototessera non conforme. ", required=False)

    def clean(self):
        stato_richiesta = self.cleaned_data['stato_richiesta']
        stato_emissione = self.cleaned_data['stato_emissione']
        motivo_rifiutato = self.cleaned_data['motivo_rifiutato']

        if stato_richiesta != Tesserino.ACCETTATO and stato_emissione:
            raise ValidationError("Puoi emettere il tesserino solo se "
                                  "accetti la richiesta di emissione. ")

        if stato_richiesta == Tesserino.RIFIUTATO and len(motivo_rifiutato) < self.MINIMO_CARATTERI_MOTIVO_RIFIUTATO:
            raise ValidationError("Rifiutando l'emissione, devi inserire una motivazione descrittiva, con almeno "
                                  "%d caratteri." % self.MINIMO_CARATTERI_MOTIVO_RIFIUTATO)


class ModuloScaricaTesserini(forms.Form):
    conferma = forms.BooleanField(help_text="Confermo di voler procedere allo scaricamento "
                                             "dei tesserini associativi.")
