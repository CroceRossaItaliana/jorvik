from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from autocomplete_light import shortcuts as autocomplete_light
from base.wysiwyg import WYSIWYGSemplice

from .models import Corso, CorsoBase, LezioneCorsoBase, PartecipazioneCorsoBase


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

    def clean_sede(self):
        sede = self.cleaned_data['sede']
        if sede.locazione is None:
            raise forms.ValidationError(
                "La Sede CRI selezionata non ha alcun indirizzo impostato. "
                "Il Presidente può modificare i dettagli della Sede, "
                "tra cui l'indirizzo della stessa.")
        return sede

    class Meta:
        model = CorsoBase
        fields = ['tipo', 'data_inizio', 'sede',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(('tipo', 'data_inizio', 'sede', 'locazione'))


class ModuloModificaLezione(ModelForm):
    class Meta:
        model = LezioneCorsoBase
        fields = ['nome', 'inizio', 'fine']

    fine = forms.DateTimeField()

    def clean(self):
        try:
            fine = self.cleaned_data['fine']
            inizio = self.cleaned_data['inizio']

        except KeyError:
            raise ValidationError("Compila correttamente tutti i campi.")

        if inizio >= fine:
            self.add_error('fine', "La fine deve essere successiva all'inizio.")


class ModuloModificaCorsoBase(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['data_inizio', 'data_esame', 'descrizione',
                  'data_attivazione', 'data_convocazione',
                  'op_attivazione', 'op_convocazione',]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }


class ModuloIscrittiCorsoBaseAggiungi(forms.Form):
    persone = autocomplete_light.ModelMultipleChoiceField("IscrivibiliCorsiAutocompletamento",
                                                          help_text="Ricerca per Codice Fiscale "
                                                                    "i Sostenitori o gli Aspiranti "
                                                                    "CRI da iscrivere a questo Corso Base.")


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
        super(ModuloVerbaleAspiranteCorsoBase, self).__init__(*args, **kwargs)

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

