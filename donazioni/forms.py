import autocomplete_light
from django.core.exceptions import ValidationError
from django import forms
from django.db import transaction

from base.utils import poco_fa
from base.wysiwyg import WYSIWYGSemplice
from donazioni.models import Campagna, Etichetta, Donazione, Donatore


class ModuloCampagna(forms.ModelForm):
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
        # aggiunge tutte le etichette provenienti dal form
        etichette_form = [e for e in self.cleaned_data['etichette']]
        for etichetta in etichette_form:
            campagna.etichette.add(etichetta)
        return campagna

    def clean(self):
        inizio = self.cleaned_data['inizio']
        fine = self.cleaned_data['fine']
        if inizio >= fine:
            raise ValidationError('La data di fine campagna deve essere posteriore a quella di inizio')


class ModuloEtichetta(forms.ModelForm):
    class Meta:
        model = Etichetta
        fields = ('nome', 'comitato')

    comitato = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                         help_text="Seleziona il comitato ricercando per nome fra le sedi "
                                                                   "di cui si ha la delega per l'organizzazione di una campagna")


class ModuloFiltraCampagnePerEtichetta(forms.Form):
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False)


class ModuloDonazione(forms.ModelForm):
    data = forms.DateTimeField(required=False)

    class Meta:
        model = Donazione
        fields = ('campagna', 'modalita', 'importo', 'codice_transazione', 'data', 'ricorrente')

    def __init__(self, *args, **kwargs):
        campagna_id = kwargs.pop('campagna')
        super().__init__(*args, **kwargs)
        self.fields['importo'].min_value = 0.0
        if campagna_id:
            self.fields['campagna'].widget = forms.HiddenInput()
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


class ModuloDonatore(forms.ModelForm):
    class Meta:
        model = Donatore
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stato_nascita'].empty_label = None


class ModuloImportDonazioni(forms.Form):
    XLS = 'xls'
    CSV = 'csv'
    FORMATI = (
        (XLS, 'Excel XLS'),
        (CSV, 'CSV')
    )
    file_da_importare = forms.FileField()
    righe_intestazione = forms.IntegerField(min_value=0, initial=1)
    formato = forms.ChoiceField(choices=FORMATI, initial=XLS)


class ModuloImportDonazioniMapping(forms.Form):
    escludi_campi = ('id', 'creazione', 'ultima_modifica',
                     'campagna', 'donatore', 'ricorrente', 'modalita')
    _campo_modello_dict = {Donatore: [f.name for f in Donatore._meta.fields],
                           Donazione: [f.name for f in Donazione._meta.fields]}

    def __init__(self, *args, **kwargs):
        self.colonne_dict = kwargs.pop('colonne')
        super().__init__(*args, **kwargs)
        campi_donazione = [("Campi Donazione", [(f.name, f.verbose_name) for f in Donazione._meta.fields if f.name not in self.escludi_campi])]
        campi_donatore = [("Campi Donatore", [(f.name, f.verbose_name) for f in Donatore._meta.fields if f.name not in self.escludi_campi])]
        campi_donazione_donatore = [('', '-----')] + campi_donazione + campi_donatore
        for col_idx, preview in self.colonne_dict.items():
            field_name = 'colonna_{index}'.format(index=col_idx)
            self.fields[field_name] = forms.ChoiceField(choices=campi_donazione_donatore, required=False)
            self.fields[field_name].help_text = 'Campo per valori: {}'.format(preview)
            self.fields[field_name].empty_label = None

    def clean(self):
        cleaned_data = super().clean()
        associazioni_definite = {campo: valore for campo, valore in cleaned_data.items() if valore}
        if not associazioni_definite or 'importo' not in associazioni_definite.values():
            raise ValidationError('Devi associare almeno il campo "Importo in EUR" ad una colonna')

        if len(set(associazioni_definite.values())) != len(associazioni_definite):
            raise ValidationError('Hai associato uno stesso campo a più di una colonna')


    @staticmethod
    def _converti(nome_campo, valore):
        """ Metodo per validare/convertire valori da stringa"""
        if nome_campo.startswith('data'):
            from dateutil.parser import parse
            valore = parse(valore, fuzzy=True)
        elif nome_campo == 'importo':
            try:
                valore = float(valore)
            except ValueError:
                # riprova per cifre del tipo 30,50 €
                valore = float(valore.replace(',', '.'))
        return valore

    def processa(self, campagna, dati_importati, test_import=True):
        # TODO metodo troppo lungo e con troppi livelli di identazione. Valutare se e come dividerlo e/o spostarlo
        """
        Questo metodo processa e inserisce in DB le righe provenienti dal file
        rappresentanti oggetti Donazione e Donatore.
        Se test_import=True, i risultati sono una simulazione dell'import.
        :param campagna: Campagna per cui si stanno importando donazioni
        :param dati_importati: righe del foglio csv/xls importato
               Il mapping numero_colonna: nome_campo è fornito dai valori dei campi del modulo
        :param test_import: True se è una prova (dal modulo Importa Donazioni)
        :return: riepilogo: dict con lista di oggetti inseriti, righe non inserite
                e righe inserite con singoli errori sui campi
        """
        data_processamento = poco_fa()
        mapping_colonne_campi = {int(f.split('_')[1]): v for f, v in self.cleaned_data.items()}
        oggetti_donazioni = []
        righe_con_campi_errati = set()
        righe_non_inserite = []
        riepilogo = {}
        try:
            with transaction.atomic():
                for riga in dati_importati:
                    argomenti = {Donatore: {}, Donazione: {}}
                    for i, valore in enumerate(riga, start=1):
                        try:
                            nome_campo = mapping_colonne_campi.get(i)
                            if nome_campo and valore:
                                modello = Donatore if nome_campo in self._campo_modello_dict[Donatore] else Donazione
                                valore = self._converti(nome_campo, valore)
                                argomenti[modello][nome_campo] = valore
                        except (ValueError, TypeError):
                            righe_con_campi_errati.add(str(riga))

                    try:
                        donazione = Donazione(**argomenti[Donazione])
                        if not donazione.importo:
                            raise ValueError('Importo donazione mancante')
                        if not donazione.data:
                            donazione.data = data_processamento
                        donazione.campagna = campagna
                        if argomenti[Donatore]:
                            donatore = Donatore(**argomenti[Donatore])
                            donatore = Donatore.nuovo_o_esistente(donatore)
                            donazione.donatore = donatore
                        oggetti_donazioni.append(donazione)

                        donazione.save()
                    except (ValueError, TypeError, ValidationError):
                        riga = str(riga)
                        righe_non_inserite.append(riga)
                        print(riga)
                        if riga in righe_con_campi_errati:
                            righe_con_campi_errati.remove(riga)

                riepilogo = {'inserite': oggetti_donazioni,
                             'non_inserite': righe_non_inserite,
                             'inserite_incomplete': righe_con_campi_errati}
                if test_import:
                    # esce dal context con un'eccezione quindi non fa il commit dei dati sul DB
                    # equivale ad un rollback
                    raise ValueError()
        except ValueError:
            pass
        return riepilogo
