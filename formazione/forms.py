from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, modelformset_factory

from autocomplete_light import shortcuts as autocomplete_light
from base.wysiwyg import WYSIWYGSemplice

from anagrafica.models import Delega, Persona
from .models import (Corso, CorsoBase, CorsoLink, CorsoFile, CorsoEstensione,
                     LezioneCorsoBase, PartecipazioneCorsoBase)


class ModuloCreazioneCorsoBase(ModelForm):
    PRESSO_SEDE = "PS"
    ALTROVE = "AL"
    LOCAZIONE = (
        (PRESSO_SEDE, "Il corso si svolgerà presso la Sede."),
        (ALTROVE, "Il corso si svolgerà altrove (specifica dopo).")
    )

    locazione = forms.ChoiceField(choices=LOCAZIONE, initial=PRESSO_SEDE,
                    help_text="La posizione del Corso è importante per "
                                "aiutare gli aspiranti a trovare i Corsi "
                                "che si svolgono vicino a loro.")

    def clean_tipo(self):
        tipo = self.cleaned_data['tipo']
        if not tipo:
            raise ValidationError('Seleziona un valore.')
        return tipo

    def clean_sede(self):
        sede = self.cleaned_data['sede']
        if sede.locazione is None:
            raise forms.ValidationError(
                "La Sede CRI selezionata non ha alcun indirizzo impostato. "
                "Il Presidente può modificare i dettagli della Sede, "
                "tra cui l'indirizzo della stessa.")
        return sede

    def clean(self):
        cd = self.cleaned_data
        if cd['data_esame'] < cd['data_inizio']:
            self.add_error('data_esame', "La data deve essere successiva "
                                         "alla data di inizio.")
        return cd

    class Meta:
        model = CorsoBase
        fields = ['tipo', 'titolo_cri', 'data_inizio', 'data_esame', 'sede',]
        help_texts = {
            # 'titolo_cri': 'Da selezionare se il tipo di corso non è Corso Base',
        }

    def __init__(self, *args, **kwargs):
        from curriculum.models import Titolo

        super().__init__(*args, **kwargs)
        self.order_fields(('tipo',  'titolo_cri', 'data_inizio', 'data_esame',
                           'sede', 'locazione'))

        self.fields['titolo_cri'].queryset = Titolo.objects.filter(
            is_active=True,
            goal__isnull=False,
            goal__unit_reference__isnull=False,
            tipo=Titolo.TITOLO_CRI,
        ).order_by('goal__unit_reference')


class ModuloModificaLezione(ModelForm):
    docente = autocomplete_light.ModelChoiceField("DocenteLezioniCorso")
    fine = forms.DateTimeField()

    def clean(self):
        cd = self.cleaned_data
        try:
            inizio = cd['inizio']
            fine = cd['fine']
        except KeyError:
            raise ValidationError("Compila correttamente tutti i campi.")

        if inizio >= fine:
            self.add_error('fine', "La fine deve essere successiva all'inizio.")

        data_inizio_corso = self.corso.data_inizio
        err_data_lt_inizio_corso = 'Data precedente alla data di inizo corso.'
        if inizio < data_inizio_corso:
            self.add_error('inizio', err_data_lt_inizio_corso)
        if fine < data_inizio_corso:
            self.add_error('fine', err_data_lt_inizio_corso)

        return cd
    
    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        super().__init__(*args, **kwargs)

    class Meta:
        model = LezioneCorsoBase
        fields = ['nome', 'docente', 'inizio', 'fine', 'obiettivo', 'luogo']


class ModuloModificaCorsoBase(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['data_inizio', 'data_esame',
                  'titolo_cri', 'min_participants', 'max_participants',
                  'descrizione',
                  'data_attivazione', 'data_convocazione',
                  'op_attivazione', 'op_convocazione',]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }

    def clean(self):
        cd = self.cleaned_data
        if 'min_participants' in cd and 'max_participants' in cd:
            min, max = cd['min_participants'], cd['max_participants']
            if min > max:
                self.add_error('min_participants', "Numero minimo di "
                    "partecipanti non può essere maggiore del numero massimo.")
            if max < min:
                self.add_error('max_participants', "Numero massimo di "
                    "partecipanti non può essere minore del numero minimo.")
        return cd

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        is_nuovo = instance.tipo == Corso.CORSO_NUOVO
        if not is_nuovo:
            self.fields.pop('min_participants')
            self.fields.pop('max_participants')
            self.fields.pop('titolo_cri')
        if is_nuovo and instance.stato == Corso.ATTIVO:
            self.fields['titolo_cri'].widget.attrs['disabled'] = 'disabled'


class CorsoLinkForm(ModelForm):
    class Meta:
        model = CorsoFile
        fields = ['file',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        acceptable_extensions = [
            'application/pdf',
            'application/msword', # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # .docx
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel', # xls
            'application/vnd.ms-powerpoint',
            'application/x-rar-compressed', 'application/octet-stream', # rar
            'application/zip', 'application/octet-stream',
            'application/x-zip-compressed', 'multipart/x-zip',
            'image/jpeg',
            'image/png',
            'text/csv',
            'application/rtf',
        ]
        self.fields['file'].widget.attrs = {'accept': ", ".join(
            acceptable_extensions)}


CorsoFileFormSet = modelformset_factory(CorsoFile, form=CorsoLinkForm, extra=1,
                                        max_num=2)


CorsoLinkFormSet = modelformset_factory(CorsoLink, fields=('link',), extra=1,
                                        max_num=2)


class ModuloIscrittiCorsoBaseAggiungi(forms.Form):
    persone = autocomplete_light.ModelMultipleChoiceField(
        "IscrivibiliCorsiAutocompletamento",
        help_text="Ricerca per Codice Fiscale i Sostenitori o gli Aspiranti CRI "
                  "da iscrivere a questo Corso.")

    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        super().__init__(*args, **kwargs)

        # Change dynamically autocomplete class, depending on Corso tipo
        if self.corso.is_nuovo_corso and 'persone' in self.fields:
            self.fields['persone'].widget.autocomplete_arg = 'InvitaCorsoNuovoAutocompletamento'


class CorsoSelectExtensionTypeForm(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['extension_type',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['extension_type'].choices = CorsoBase.EXTENSION_TYPE_CHOICES

        if not self.instance.get_extensions(is_active=True).count():
            # Useful to set EXT_MIA_SEDE as select's default value to avoid
            # possible issues with ExtensionFormSet
            self.initial['extension_type'] = CorsoBase.EXT_MIA_SEDE


class CorsoExtensionForm(ModelForm):
    titolo = autocomplete_light.ModelMultipleChoiceField(
        "EstensioneLivelloRegionaleTitolo", required=False)
    sede = autocomplete_light.ModelMultipleChoiceField(
        "EstensioneLivelloRegionaleSede", required=False)

    class Meta:
        model = CorsoEstensione
        fields = ['segmento', 'titolo', 'sede', 'sedi_sottostanti',]

    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        super().__init__(*args, **kwargs)


CorsoSelectExtensionFormSet = modelformset_factory(CorsoEstensione, extra=1,
    max_num=3, form=CorsoExtensionForm, can_delete=True)


class ModuloConfermaIscrizioneCorsoBase(forms.Form):
    conferma_1 = forms.BooleanField(label="Ho incontrato questo aspirante, ad esempio alla presentazione del "
                                    "corso, e mi ha chiesto di essere iscritto al Corso.")
    conferma_2 = forms.BooleanField(label="Confermo di voler iscrivere questo aspirante al Corso e comprendo che "
                                    "questa azione non sarà facilmente reversibile. Sarà comunque possibile "
                                    "non ammettere l'aspirante all'esame, qualora dovesse non presentarsi "
                                    "al resto delle lezioni (questo sarà verbalizzato).")


class ModuloVerbaleAspiranteCorsoBase(ModelForm):
    GENERA_VERBALE = 'genera_verbale'
    SALVA_SOLAMENTE = 'salva'

    class Meta:
        model = PartecipazioneCorsoBase
        fields = [
            'ammissione', 'motivo_non_ammissione',
            'esito_parte_1', 'argomento_parte_1',
            'esito_parte_2', 'argomento_parte_2',
            'extra_1', 'extra_2',
            'destinazione',
        ]

    def __init__(self, *args, generazione_verbale=False, **kwargs):
        self.generazione_verbale = generazione_verbale
        super().__init__(*args, **kwargs)

        if not self.instance.corso.is_nuovo_corso:
            # This field is not required if Corso Nuovo
            self.fields.pop('destinazione')

    def clean(self):
        """
        Qui va tutta la logica di validazione del modulo di generazione
         del verbale del corso base.
        """

        ammissione = self.cleaned_data['ammissione']
        motivo_non_ammissione = self.cleaned_data['motivo_non_ammissione']
        esito_parte_1 = self.cleaned_data['esito_parte_1']
        argomento_parte_1 = self.cleaned_data['argomento_parte_1']
        esito_parte_2 = self.cleaned_data['esito_parte_2']
        argomento_parte_2 = self.cleaned_data['argomento_parte_2']
        extra_1 = self.cleaned_data['extra_1']
        extra_2 = self.cleaned_data['extra_2']
        destinazione = self.cleaned_data['destinazione']

        # Controlla che non ci siano conflitti (incoerenze) nei dati.
        if ammissione != PartecipazioneCorsoBase.NON_AMMESSO:
            if motivo_non_ammissione:
                self.add_error('motivo_non_ammissione', "Questo campo deve essere compilato solo "
                                                        "nel caso di NON AMMISSIONE.")

        # Se non è stato ammesso, un bel gruppo di campi NON devono essere compilati.
        if ammissione != PartecipazioneCorsoBase.AMMESSO:
            da_non_compilare = ['esito_parte_1', 'argomento_parte_1', 'esito_parte_2',
                                'extra_1', 'extra_2',]
            for campo in da_non_compilare:
                if self.cleaned_data[campo]:
                    self.add_error(campo, "Questo campo deve essere compilato solo nel caso di AMMISSIONE.")

        # Controllo sulla parte 2 del corso
        if esito_parte_2 and extra_2:
            self.add_error('extra_2', "Hai specificato l'esito per la parte 2. Rimuovi l'esito "
                                      "della parte due, oppure rimuovi questa opzione.")

        if esito_parte_2 and not argomento_parte_2:
            self.add_error('argomento_parte_2', "Devi specificare l'argomento della seconda parte.")

        if ammissione == PartecipazioneCorsoBase.AMMESSO:
            if not esito_parte_1:
                self.add_error('esito_parte_1', "Devi specificare l'esito di questa parte.")

            if not argomento_parte_1:
                self.add_error('argomento_parte_1', "Devi specificare l'argomento della prima parte.")

            if (not esito_parte_2) and (not extra_2):
                self.add_error('esito_parte_2', "Devi specificare l'esito di questa parte oppure "
                                                "selezionare l'opzione per specificare che l'esame "
                                                "non includeva questa parte.")

        if ammissione == PartecipazioneCorsoBase.NON_AMMESSO:
            if not motivo_non_ammissione:
                self.add_error('motivo_non_ammissione', "Devi specificare la motivazione di non "
                                                        "ammissione all'esame.")

        # Se sto generando il verbale, controlla che tutti i campi
        # obbligatori siano stati riempiti.
        if self.generazione_verbale:
            if not destinazione:
                self.add_error('destinazione',
                               "È necessario selezionare la Sede presso la quale il Volontario "
                               "diventerà Volontario (nel solo caso di superamento dell'esame).")


class FormCreateDirettoreDelega(ModelForm):
    persona = autocomplete_light.ModelChoiceField('CreateDirettoreDelegaAutocompletamento')

    class Meta:
        model = Delega
        fields = ['persona',]

    def __init__(self, *args, **kwargs):
        # These attrs are passed in anagrafica.viste.strumenti_delegati()
        for attr in ['me', 'course']:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))
        super().__init__(*args, **kwargs)


class InformCourseParticipantsForm(forms.Form):
    ALL = '1'
    UNCONFIRMED_REQUESTS = '2'
    CONFIRMED_REQUESTS = '3'
    INVIA_QUESTIONARIO = '4'

    message = forms.CharField(label='Messaggio', required=True, max_length=3000)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')

        CHOICES = [
            (self.ALL, "A tutti (già iscritti + chi ha fatto richiesta)"),
            (self.UNCONFIRMED_REQUESTS, 'Solo a chi ha fatto richieste'),
            (self.CONFIRMED_REQUESTS, 'Partecipanti confermati'),
        ]

        if self.instance.concluso:
            CHOICES.append((self.INVIA_QUESTIONARIO,
                            "Invia questionario di gradimento ai partecipanti"))

        super().__init__(*args, **kwargs)
        self.fields['recipient_type'] = forms.ChoiceField(choices=CHOICES, label='Destinatari')
