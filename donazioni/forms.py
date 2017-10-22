from io import StringIO
from dateutil.parser import parse
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django import forms
from django.db import transaction
from django.db.utils import DataError
from django.utils.translation import ugettext_lazy as _

from django_countries.data import COUNTRIES
import autocomplete_light

from base.utils import poco_fa
from base.wysiwyg import WYSIWYGSemplice
from donazioni.models import Campagna, Etichetta, Donazione, Donatore
from donazioni.utils_importazione import colnum_string, FormatoImport, FormatoImportPredefinito


class ModuloCampagna(forms.ModelForm):
    class Meta:
        model = Campagna
        fields = ('inizio', 'fine', 'nome', 'descrizione', 'organizzatore',
                  'testo_email_ringraziamento', 'permetti_scaricamento_ricevute')
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
        campagna = kwargs.get('instance')
        if campagna:
            # aggiunge kwargs['initial'] per inizializzare le etichette in modifica
            initial = kwargs.setdefault('initial', {})
            initial['etichette'] = kwargs['instance'].etichette.all()

        super().__init__(*args, **kwargs)
        if campagna and not campagna.date_modificabili:
            self.fields['inizio'].widget.attrs['readonly'] = True
            self.fields['fine'].widget.attrs['readonly'] = True
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
        if self.instance and not self.instance.date_modificabili and any(x in self.changed_data for x in ('inizio', 'fine')):
            raise ValidationError('Le date di inizio e fine campagna non sono più modificabili')
        inizio = self.cleaned_data.get('inizio')
        fine = self.cleaned_data.get('fine')
        if not inizio or not fine:
            self._errors['inizio'] = self.error_class(['Le date di inizio e fine campagna sono dati obbligatori'])
            self._errors['fine'] = self.error_class(['Le date di inizio e fine campagna sono dati obbligatori'])
            raise ValidationError('Le date di inizio e fine campagna sono dati obbligatori')
        if inizio >= fine:
            self._errors['inizio'] = self.error_class(['La data di fine campagna deve essere posteriore a quella di inizio'])
            self._errors['fine'] = self.error_class(['La data di fine campagna deve essere posteriore a quella di inizio'])
            raise ValidationError('La data di fine campagna deve essere posteriore a quella di inizio')
        return self.cleaned_data


class ModuloEtichetta(forms.ModelForm):
    class Meta:
        model = Etichetta
        fields = ('slug', 'comitato')

    comitato = autocomplete_light.forms.ModelChoiceField('SedeDonazioniAutocompletamento',
                                                         help_text="Seleziona il comitato ricercando per nome fra le sedi "
                                                                   "di cui si ha la delega per l'organizzazione di una campagna")


class ModuloFiltraCampagnePerEtichetta(forms.Form):
    etichette = autocomplete_light.forms.ModelMultipleChoiceField('EtichettaAutocompletamento', required=False)


class ModuloDonazione(forms.ModelForm):
    data = forms.DateTimeField(required=False)

    class Meta:
        model = Donazione
        fields = ('campagna', 'metodo_pagamento', 'importo', 'codice_transazione',
                  'data', 'modalita_singola_ricorrente', 'permetti_scaricamento_ricevute')

    def __init__(self, *args, **kwargs):
        campagna_id = kwargs.pop('campagna')
        super().__init__(*args, **kwargs)
        self.fields['importo'].min_value = 0.1

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
            self._errors['data'] = self.error_class(["La data della donazione deve essere compresa fra l'inizio e la fine della campagna"])
            raise ValidationError("La data della donazione deve essere compresa fra l'inizio e la fine della campagna")
        if data_donazione > poco_fa():
            self._errors['data'] = self.error_class(["La data della donazione non può essere una data nel futuro"])
            raise ValidationError("La data della donazione non può essere una data nel futuro")
        return self.cleaned_data


class ModuloDonatore(forms.ModelForm):

    class Meta:
        model = Donatore
        exclude = ('periodico',)

    def __init__(self, *args, **kwargs):
        nuova_donazione = kwargs.pop('nuova_donazione', False)
        super().__init__(*args, **kwargs)
        self.fields['stato_nascita'].empty_label = None
        if nuova_donazione:
            self.fields['invia_email'] = forms.BooleanField(help_text='Invia una mail di ringraziamento nel caso '
                                                                      'il donatore fornisca un indirizzo email')
            self.fields['invia_email'].initial = True

    def clean(self):
        super().clean()
        data_nascita = self.cleaned_data.get('data_nascita')
        if data_nascita and data_nascita > poco_fa().date():
            self._errors['data_nascita'] = self.error_class(["Data di nascita del donatore non valida"])
            raise ValidationError("Data di nascita del donatore non valida")
        return self.cleaned_data


class ModuloInviaNotifica(forms.Form):
    invia = forms.BooleanField(widget=forms.HiddenInput(),
                               required=False,
                               initial=True)


class ModuloImportDonazioni(forms.Form):
    XLS = 'xls'
    CSV = 'csv'
    FORMATI = (
        (XLS, 'Excel XLS'),
        (CSV, 'CSV')
    )
    VIRGOLA = ','
    PUNTO_VIRGOLA = ';'
    TAB = '\t'
    DELIMITATORI = (
        ('', '-----'),
        (VIRGOLA, 'Virgola ","'),
        (PUNTO_VIRGOLA, 'Punto e virgola ";"'),
        (TAB, 'Tabulatore'),
    )
    PAYPAL = 'P'
    AMMADO = 'A'
    AMAZON = 'Z'
    CRI = 'R'
    POSTE = 'O'
    SORGENTI = (
        ('', '-----'),
        (PAYPAL, 'PayPal'),
        (AMMADO, 'Ammado'),
        (AMAZON, 'Amazon'),
        (CRI, 'CRI.it'),
        # (POSTE, 'Poste'),
    )
    file_da_importare = forms.FileField(help_text='Scegli il file da importare')
    righe_intestazione = forms.IntegerField(min_value=0, initial=1, help_text='Numero di righe prima dei dati veri e propri')
    formato = forms.ChoiceField(choices=FORMATI, initial=XLS, help_text='Formato del file (CSV per formato testo con separatore '
                                                                        'o XLS per file Excel di Microsoft')
    delimitatore_csv = forms.ChoiceField(choices=DELIMITATORI, required=False, help_text='Scegli il separatore (soltanto '
                                                                                         'nel caso di file CSV)')
    sorgente = forms.ChoiceField(choices=SORGENTI, required=False,
                                 help_text='Se il file è un esportazione di dati proveniente da una particolare'
                                           ' piattaforma online di donazioni (e.g. PayPal), puoi definire qui '
                                           'la sorgente. In tal modo, il mapping fra colonne e campi della prossima schermata sarà'
                                           ' predefinito e non occorrerà farlo a mano')


class ModuloImportDonazioniMapping(forms.Form):
    campi_da_convertire = ('sesso', 'tipo_donatore', 'data', 'data_nascita',
                           'stato_nascita', 'stato_residenza', 'importo',
                           'metodo_pagamento', 'modalita_singola_ricorrente')
    valori_nulli = ('-', ' ', '')
    valori_sesso_maschile = ('maschio', 'm', 'maschile', 'uomo')
    valori_sesso_femminile = ('femmina', 'f', 'femminile', 'donna')
    escludi_campi = ('id', 'creazione', 'ultima_modifica', 'campagna', 'donatore',)
    nazioni_codici_dict = {v.lower(): k for k, v in COUNTRIES.items()}

    _campo_modello_dict = {Donatore: [f.name for f in Donatore._meta.fields],
                           Donazione: [f.name for f in Donazione._meta.fields]}

    def __init__(self, *args, **kwargs):
        self.colonne_dict = kwargs.pop('colonne')
        self.intestazione = kwargs.pop('intestazione', 0)
        self.sorgente = kwargs.pop('sorgente', '')
        self.metodo_pagamento_da_colonna = False
        super().__init__(*args, **kwargs)
        campi_donazione = [
            ('Campi Donazione', [(f.name, f.verbose_name) for f in Donazione._meta.fields if f.name not in self.escludi_campi])
        ]
        campi_donatore = [('Campi Donatore', [(f.name, f.verbose_name) for f in Donatore._meta.fields if f.name not in self.escludi_campi])]
        campi_donazione_donatore = [('', '-----')] + campi_donazione + campi_donatore
        campi_definiti_con_sorgente = FormatoImportPredefinito.formati.get(self.sorgente, FormatoImport)().campi_definiti
        for nome_colonna, preview in self.colonne_dict.items():
            nome_campo = 'colonna_{nome_colonna}'.format(nome_colonna=nome_colonna)
            # nome_campo ha formato 'colonna_X TitoloColonnaExcel'
            self.fields[nome_campo] = forms.ChoiceField(choices=campi_donazione_donatore, required=False)
            self.fields[nome_campo].help_text = 'Campo per valori: {}'.format(preview)
            self.fields[nome_campo].empty_label = None
            self.fields[nome_campo].label = 'Colonna {}'.format(nome_colonna)
            if self.sorgente and nome_campo in campi_definiti_con_sorgente:
                self.fields[nome_campo].widget.attrs['readonly'] = 'readonly'
            elif self.sorgente and nome_campo not in campi_definiti_con_sorgente:
                self.fields[nome_campo].widget.attrs['disabled'] = 'disabled'
                self.fields[nome_campo].disabled = True

        if self.sorgente:
            # formato predefinito
            associazioni_predefinite = FormatoImportPredefinito.formati.get(self.sorgente, {}).associazioni
            for nome_campo, campo_modello in associazioni_predefinite.items():
                self.fields[nome_campo].initial = campo_modello
                if campo_modello == 'metodo_pagamento':
                    self.metodo_pagamento_da_colonna = True

    def clean(self):
        cleaned_data = super().clean()
        associazioni_definite = {campo: valore for campo, valore in cleaned_data.items() if valore}
        if not associazioni_definite:
            raise ValidationError('Non hai associato nessuna colonna ad un campo Donazione/Donatore')
        if self.sorgente not in (ModuloImportDonazioni.AMAZON,) and 'importo' not in associazioni_definite.values():
            raise ValidationError('Devi associare almeno il campo "Importo in EUR" ad una colonna')

        if len(set(associazioni_definite.values())) != len(associazioni_definite):
            raise ValidationError('Hai associato uno stesso campo a più di una colonna')
        return self.cleaned_data

    @staticmethod
    def _converti(nome_campo, valore):
        """ Metodo per validare/convertire valori da stringa"""
        print(valore, type(valore))
        print(nome_campo, '\n')
        if isinstance(valore, str):
            valore.replace('"', '').strip()
        if nome_campo not in ModuloImportDonazioniMapping.campi_da_convertire:
            return valore
        elif not valore or valore in ModuloImportDonazioniMapping.valori_nulli:
            return ''
        elif nome_campo.startswith('data'):
            if isinstance(valore, (date, datetime)):
                return valore
            return parse(valore, fuzzy=True)
        elif nome_campo.startswith('stato'):
            return ModuloImportDonazioniMapping._converti_stato(valore)
        else:
            return getattr(ModuloImportDonazioniMapping, '_converti_{}'.format(nome_campo))(valore)

    @staticmethod
    def _converti_importo(valore):
        if isinstance(valore, (int, float)):
            return valore

        if not valore or valore in ModuloImportDonazioniMapping.valori_nulli:
            return 0
        valore = valore.replace(',', '.')
        valore = float(valore)
        return valore

    @staticmethod
    def _converti_sesso(valore):
        if valore.lower() in ModuloImportDonazioniMapping.valori_sesso_maschile:
            valore = 'M'
        elif valore.lower() in ModuloImportDonazioniMapping.valori_sesso_femminile:
            valore = 'F'
        else:
            valore = ''
        return valore

    @staticmethod
    def _converti_tipo_donatore(valore):
        valore = valore.lower()
        if 'persona' in valore or 'privato' in valore:
            valore = 'P'
        elif 'azienda' in valore:
            valore = 'A'
        elif 'croce rossa' in valore or 'cri' in valore:
            valore = 'C'
        else:
            valore = 'P'
        return valore

    @staticmethod
    def _converti_stato(valore):
        if valore in COUNTRIES:
            return valore
        valore = valore.lower()
        codice_stato = ModuloImportDonazioniMapping.nazioni_codici_dict.get(_(valore))
        return codice_stato or ''

    @staticmethod
    def _converti_metodo_pagamento(valore):
        valore = valore.lower()
        if 'paypal' in valore:
            valore = 'P'
        elif 'ammado' in valore:
            valore = 'A'
        elif 'amazon' in valore:
            valore = 'Z'
        elif 'credit' in valore or 'debit' in valore:
            valore = 'B'
        else:
            valore = ''
        return valore

    @staticmethod
    def _converti_modalita_singola_ricorrente(valore):
        valore = valore.lower()
        if 'unic' in valore or 'singola' in valore:
            valore = 'S'
        elif 'ricorrente' in valore:
            valore = 'R'
        else:
            valore = ''
        return valore

    def processa(self, campagna, dati_importati, test_import=True):
        # TODO metodo troppo lungo e con troppi livelli di identazione!
        # ### Valutare se e come dividerlo e/o spostarlo
        """
        Questo metodo processa e inserisce in DB le righe provenienti dal file
        rappresentanti oggetti Donazione e Donatore.
        Se test_import=True, i risultati sono una simulazione dell'import.
        :param campagna: Campagna per cui si stanno importando donazioni
        :param dati_importati: righe del foglio csv/xls importato
               Il mapping nome_colonna: nome_campo è fornito dai valori dei campi del modulo
        :param test_import: True se è una prova (dal modulo Importa Donazioni)
        :return: riepilogo: dict con lista di oggetti inseriti, righe non inserite
                e righe inserite con singoli errori sui campi
        """
        data_processamento = poco_fa()
        # f = 'colonna_O NomeNazione'
        # v = 'stato_residenza'
        mapping_colonne_campi = {f.split()[0].split('_')[1]: v for f, v in self.cleaned_data.items()}

        oggetti_donazioni = []
        oggetti_donatori = set()
        righe_con_campi_errati = set()
        righe_non_inserite = []
        riepilogo = {}

        try:
            with transaction.atomic():
                riepilogo_errori = StringIO()
                for numero_riga, riga in enumerate(dati_importati, start=1 + self.intestazione):
                    argomenti = {Donatore: {}, Donazione: {}}
                    for i, valore in enumerate(riga):
                        try:
                            nome_campo = mapping_colonne_campi.get(colnum_string(i))
                            if nome_campo and valore:
                                modello = Donatore if nome_campo in self._campo_modello_dict[Donatore] else Donazione
                                valore = self._converti(nome_campo, valore)
                                argomenti[modello][nome_campo] = valore
                        except (ValueError, TypeError) as exc:
                            riga = str(riga)
                            riepilogo_errori.write('<li>Riga {} {}: {}</li>'.format(numero_riga, riga, exc))
                            righe_con_campi_errati.add(str(riga))

                    try:
                        donazione = None
                        donatore = None
                        if argomenti[Donazione] and argomenti[Donazione].get('importo', 0) >= 0:
                            if self.sorgente and not self.metodo_pagamento_da_colonna:
                                # sorgente predefinita che non contiene una colonna Metodo Pagamento
                                # in tal caso, il metodo pagamento viene sovrascritto con la sorgente
                                # (e.g. PayPal)
                                argomenti[Donazione]['metodo_pagamento'] = self.sorgente
                            donazione = Donazione(**argomenti[Donazione])
                            if not donazione.data:
                                donazione.data = data_processamento
                            donazione.campagna = campagna
                        if argomenti[Donatore]:
                            donatore = Donatore(**argomenti[Donatore])
                            donatore = Donatore.nuovo_o_esistente(donatore)
                            oggetti_donatori.add(donatore)

                        if donazione:
                            oggetti_donazioni.append(donazione)
                            if donatore:
                                donazione.donatore = donatore
                            donazione.save()

                    except (ValueError, TypeError, ValidationError, DataError) as exc:
                        riga = str(riga)
                        righe_non_inserite.append(riga)
                        if riga in righe_con_campi_errati:
                            righe_con_campi_errati.remove(riga)
                        riepilogo_errori.write('<li><b>Riga {}</b> {}: {}</li>'.format(numero_riga, riga, exc))

                riepilogo = {'donazioni_inserite': oggetti_donazioni,
                             'donatori_inseriti': oggetti_donatori,
                             'non_inserite': righe_non_inserite,
                             'inserite_incomplete': righe_con_campi_errati,
                             'errori': riepilogo_errori.getvalue()}
                if test_import:
                    # In caso di Test Importazione esce dal context con un'eccezione quindi non fa il commit dei dati sul DB
                    # equivale ad un rollback
                    raise ValueError()
        except ValueError:
            # Rollback in caso di errori
            pass
        return riepilogo
