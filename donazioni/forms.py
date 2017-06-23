import autocomplete_light
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, HiddenInput, DateTimeField

from base.wysiwyg import WYSIWYGSemplice
from donazioni.models import Campagna, Etichetta, Donazione, Donatore


class ModuloCampagna(ModelForm):
    class Meta:
        model = Campagna
        fields = ('inizio', 'fine', 'nome', 'descrizione', 'organizzatore')
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }

    organizzatore = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                              help_text="Ricerca per nome fra le sedi di cui si ha la delega "
                                                                        "per l'organizzazione di una campagna")
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False,
                                                                  help_text='Ricerca per nome fra le etichette del comitato'
                                                                            ' e quelle del Comitato Nazionale.')

    def __init__(self, *args, **kwargs):
        # instance: Campagna
        if kwargs.get('instance'):
            # aggiunge kwargs['initial'] per inizializzare le etichette in modifica
            initial = kwargs.setdefault('initial', {})
            initial['etichette'] = kwargs['instance'].etichette.all()
        super().__init__(*args, **kwargs)
        self.fields['inizio'].required = True
        self.fields['fine'].required = True

    def save(self, commit=True):
        campagna = super().save()  # salva campagna (e aggiunge etichetta di default)
        # rimuovi tutte le etichette (tranne quella di default)
        campagna.etichette.remove(*list(campagna.etichette.filter(default=False)))
        # aggiunge tutte le etichette proveniente dal form (tranne quella di default, se presente)
        etichette_form = [e for e in self.cleaned_data['etichette'] if not e.default]
        for etichetta in etichette_form:
            campagna.etichette.add(etichetta)
        return campagna

    def clean(self):
        inizio = self.cleaned_data['inizio']
        fine = self.cleaned_data['fine']
        if inizio >= fine:
            raise ValidationError('La data di fine campagna deve essere posteriore a quella di inizio')


class ModuloEtichetta(ModelForm):
    class Meta:
        model = Etichetta
        fields = ('nome', 'comitato')

    comitato = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                         help_text="Ricerca per nome fra le sedi di cui si ha la delega "
                                                                   "per l'organizzazione di una campagna")


class ModuloFiltraCampagnePerEtichetta(Form):
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False)


class ModuloDonazione(ModelForm):
    data = DateTimeField(required=False)

    class Meta:
        model = Donazione
        fields = ('campagna', 'modalita', 'importo', 'data', 'ricorrente')

    def __init__(self, *args, **kwargs):
        campagna_id = kwargs.pop('campagna')
        super().__init__(*args, **kwargs)
        self.fields['importo'].min_value = 0.0
        if campagna_id:
            self.fields['campagna'].widget = HiddenInput()
            self.fields['campagna'].widget.attrs['readonly'] = True
            self.fields['campagna'].initial = campagna_id
            self.fields['campagna'].queryset = Campagna.objects.filter(id=campagna_id)

    def clean(self):
        data_donazione = self.cleaned_data['data']
        if not data_donazione:
            return
        campagna = self.cleaned_data['campagna']
        if not campagna.inizio <= data_donazione <= campagna.fine:
            raise ValidationError("La data della donazione deve essere compresa fra l'inizio e la fine della campagna")


class ModuloDonatore(ModelForm):
    class Meta:
        model = Donatore
        fields = ('nome', 'cognome', 'email', 'codice_fiscale', 'ragione_sociale',
                  'data_nascita', 'comune_nascita', 'provincia_nascita', 'stato_nascita')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stato_nascita'].empty_label = None
