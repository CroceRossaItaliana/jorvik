from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, modelformset_factory

from autocomplete_light import shortcuts as autocomplete_light
from base.wysiwyg import WYSIWYGSemplice

from anagrafica.permessi import applicazioni as permessi
from anagrafica.costanti import LOCALE, REGIONALE, NAZIONALE
from anagrafica.models import Delega, Persona
from curriculum.models import Titolo
from curriculum.areas import OBBIETTIVI_STRATEGICI
from .models import (Corso, CorsoBase, CorsoLink, CorsoFile, CorsoEstensione,
                     LezioneCorsoBase, PartecipazioneCorsoBase)


class ModuloCreazioneCorsoBase(ModelForm):
    PRESSO_SEDE = "PS"
    ALTROVE = "AL"
    LOCAZIONE = (
        (PRESSO_SEDE, "Il corso si svolgerà presso la Sede."),
        (ALTROVE, "Il corso si svolgerà altrove (specifica dopo).")
    )

    DEFAULT_BLANK_LEVEL = ('', '---------'),
    LEVELS_CHOICES = ()

    level = forms.ChoiceField(choices=LEVELS_CHOICES, label='Livello', required=False)
    area = forms.ChoiceField(choices=OBBIETTIVI_STRATEGICI, label='Settore di riferimento', required=False)
    locazione = forms.ChoiceField(choices=LOCAZIONE, initial=PRESSO_SEDE, label='Sede del Corso',)
    titolo_cri = forms.ChoiceField(label='Titolo del Corso', required=False)

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

    def clean_delibera_file(self):
        cd = self.cleaned_data['delibera_file']
        return cd

    def clean(self):
        cd = self.cleaned_data
        tipo = cd['tipo']

        if cd['data_esame'] < cd['data_inizio']:
            self.add_error('data_esame', "La data deve essere successiva "
                                         "alla data di inizio.")

        if tipo == Corso.BASE:
            # cd non può/deve avere valori per questi campi se corso è BASE
            for field in ['area', 'level', 'titolo_cri']:
                if field in cd:
                    del cd[field]

        if tipo == Corso.CORSO_NUOVO:
            cd_titolo_cri = cd.get('titolo_cri')

            if not cd_titolo_cri:
                self.add_error('titolo_cri',
                    "Seleziona un titolo per il Corso (l'elenco dei titoli "
                    "si genera sulla base dell'area selezionata)")
            else:
                cd['titolo_cri'] = Titolo.objects.get(id=cd_titolo_cri)

            if not cd['area']:
                self.add_error('area', 'Seleziona area del Corso')
            if not cd['level']:
                self.add_error('level', 'Seleziona livello del Corso')

        return cd

    class Meta:
        model = CorsoBase
        fields = ['tipo', 'level', 'titolo_cri', 'data_inizio', 'data_esame',
                  'delibera_file', 'sede',]
        help_texts = {
            'sede': 'Inserire il Comitato CRI che organizza il Corso',
        }
        labels = {
            'sede': 'Comitato CRI',
        }

    def __init__(self, *args, **kwargs):
        from curriculum.models import Titolo

        me = kwargs.pop('me')

        super().__init__(*args, **kwargs)
        self.order_fields(('tipo', 'level', 'area', 'titolo_cri', 'data_inizio',
            'data_esame', 'delibera_file', 'sede', 'locazione'))

        # GAIA-16
        delega = me.deleghe_attuali().filter(tipo__in=[permessi.PRESIDENTE,
                                                       permessi.RESPONSABILE_FORMAZIONE]).last()
        if delega:
            estensione_sede = delega.sede.all().first().estensione

            levels = 2
            if estensione_sede == LOCALE:
                pass
            elif estensione_sede == REGIONALE:
                levels = 3
            elif estensione_sede == NAZIONALE:
                levels = 4

        self.fields['level'].choices = Titolo.CDF_LIVELLI[:levels]
        self.fields['area'].choices = list(self.DEFAULT_BLANK_LEVEL) + self.fields['area'].choices
        self.fields['titolo_cri'].choices = list(self.DEFAULT_BLANK_LEVEL) + [
            (choice.pk, choice) for choice in Titolo.objects.filter(
                area__isnull=False,
                nome__isnull=False,
                tipo=Titolo.TITOLO_CRI,
                is_active=True,
            ).order_by('nome')]

        # Sort area options 'ASC'
        self.fields['area'].choices = sorted(self.fields['area'].choices, key=lambda x: x[1])


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
                  'min_participants', 'max_participants',
                  'descrizione',
                  'data_attivazione', 'data_convocazione',]
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

        # The fields are commented because the field's logic was moved to ModuloCreazioneCorsoBase forms step
            # self.fields.pop('titolo_cri')
        # if is_nuovo and instance.stato == Corso.ATTIVO:
        #     self.fields['titolo_cri'].widget.attrs['disabled'] = 'disabled'


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
        labels = {
            'extension_type': "Tipo dell'estensione",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['extension_type'].choices = CorsoBase.EXTENSION_TYPE_CHOICES

        if not self.instance.get_extensions(is_active=True).count():
            # Useful to set EXT_MIA_SEDE as select's default value to avoid
            # possible issues with ExtensionFormSet
            self.initial['extension_type'] = CorsoBase.EXT_MIA_SEDE


class CorsoExtensionForm(ModelForm):
    titolo = autocomplete_light.ModelMultipleChoiceField(
        "EstensioneLivelloRegionaleTitolo", required=False, label='Requisiti necessari')
    sede = autocomplete_light.ModelMultipleChoiceField(
        "EstensioneLivelloRegionaleSede", required=False, label='Selezionare Sede/Sedi')

    class Meta:
        model = CorsoEstensione
        fields = ['segmento', 'titolo', 'sede', 'sedi_sottostanti',]
        labels = {
            'segmento': "Destinatari del Corso",
        }

    def clean(self):
        cd = self.cleaned_data

        if self.corso:
            if self.corso.titolo_cri in cd['titolo']:
                self.add_error('titolo', "Non è possibile selezionare lo stesso titolo del Corso.")

        return cd

    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        super().__init__(*args, **kwargs)

        # if self.corso.is_nuovo_corso and self.corso.titolo_cri:
        #     self.fields['titolo'].initial = Titolo.objects.filter(id__in=[
        #         self.corso.titolo_cri.pk])


CorsoSelectExtensionFormSet = modelformset_factory(CorsoEstensione, extra=1,
    max_num=3, form=CorsoExtensionForm, can_delete=True)


class ModuloConfermaIscrizioneCorso(forms.Form):
    IS_CORSO_NUOVO = True


class ModuloConfermaIscrizioneCorsoBase(forms.Form):
    conferma_1 = forms.BooleanField(
        label="Ho incontrato questo aspirante, ad esempio alla presentazione del corso, e mi ha chiesto di essere iscritto al Corso.")
    conferma_2 = forms.BooleanField(
        label="Confermo di voler iscrivere questo aspirante al Corso e comprendo che "
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

        if self.instance.corso.is_nuovo_corso:
            # This field is not required if Corso Nuovo
            self.fields.pop('destinazione')

    def clean(self):
        """
        Qui va tutta la logica di validazione del modulo di generazione
         del verbale del corso base.
        """

        cd = super().clean()

        ammissione = cd['ammissione']
        motivo_non_ammissione = cd['motivo_non_ammissione']
        esito_parte_1 = cd['esito_parte_1']
        argomento_parte_1 = cd['argomento_parte_1']
        esito_parte_2 = cd['esito_parte_2']
        argomento_parte_2 = cd['argomento_parte_2']
        extra_1 = cd['extra_1']
        extra_2 = cd['extra_2']
        destinazione = cd.get('destinazione')

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


        # Se sto generando il verbale, controlla che tutti i campi obbligatori siano stati riempiti.
        if self.generazione_verbale:
            if not destinazione and not self.instance.corso.is_nuovo_corso:
                self.add_error('destinazione',
                   "È necessario selezionare la Sede presso la quale il Volontario "
                   "diventerà Volontario (nel solo caso di superamento dell'esame)."
                )


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
