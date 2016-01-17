import datetime

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Estensione, ProvvedimentoDisciplinare, Delega, \
    Fototessera, Trasferimento, Riserva
from autenticazione.models import Utenza
import autocomplete_light

from curriculum.models import TitoloPersonale
from sangue.models import Donatore, Donazione


class ModuloStepComitato(autocomplete_light.ModelForm):
    class Meta:
        model = Appartenenza
        fields = ['sede', 'inizio', ]

    inizio = forms.DateField(label="Data di Ingresso in CRI")


class ModuloStepCodiceFiscale(ModelForm):

    class Meta:
        model = Persona
        fields = ['codice_fiscale', ]

    # Effettua dei controlli personalizzati sui sui campi
    def clean(self):
        cleaned_data = self.cleaned_data

        # Fa il controllo di univocita' sul CF
        codice_fiscale = cleaned_data.get('codice_fiscale')
        if Persona.objects.filter(codice_fiscale=codice_fiscale).exists():  # Esiste gia'?
            self._errors['codice_fiscale'] = self.error_class(['Questo codice fiscale esiste in Gaia.'])

        return cleaned_data


class ModuloStepCredenziali(forms.Form):
    email = forms.EmailField(help_text="Deve essere un indirizzo e-mail personale sotto il tuo solo controllo.")
    password = forms.CharField(help_text="Scegli una password complessa per proteggere la tua privacy.", widget=forms.PasswordInput)
    ripeti_password = forms.CharField(widget=forms.PasswordInput)

    # Effettua dei controlli personalizzati sui sui campi
    def clean(self):
        cleaned_data = self.cleaned_data

        # Fa il controllo di univocita' sull'indirizzo e-mail
        email = cleaned_data.get('email')
        if Utenza.objects.filter(email=email).exists():  # Esiste gia'?
            self._errors['email'] = self.error_class(['Questa e-mail esiste in Gaia.'])

        # Fa il controllo di univocita' sull'indirizzo e-mail
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('ripeti_password')
        if password != password2:
            self._errors['password'] = self.error_class(['La password digitata non corrisponde.'])
            self._errors['ripeti_password'] = self.error_class(['La password digitata non corrisponde.'])

        if len(password) < Utenza.MIN_PASSWORD_LENGTH:
            self._errors['password'] = self.error_class(["La password deve avere almeno %d caratteri." % (Utenza.MIN_PASSWORD_LENGTH,)])

        # TODO Controllo robustezza password

        return cleaned_data


class ModuloStepAnagrafica(ModelForm):
    class Meta:
        model = Persona
        fields = ['nome', 'cognome', 'data_nascita', 'comune_nascita', 'provincia_nascita', 'stato_nascita',
                  'codice_fiscale',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza', 'stato_residenza',
                  'cap_residenza', 'conoscenza', ]

    def clean_codice_fiscale(self):
        codice_fiscale = self.cleaned_data.get('codice_fiscale')
        # Qui si potrebbe controllare la validita' del codice fiscale,
        #  cosa che attualmente abbiamo deciso di non fare.
        return codice_fiscale


class ModuloModificaAnagrafica(ModelForm):
    class Meta:
        model = Persona
        fields = ['comune_nascita', 'provincia_nascita', 'stato_nascita',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza', 'stato_residenza',
                  'cap_residenza',]


class ModuloProfiloModificaAnagrafica(ModelForm):
    class Meta:
        model = Persona
        fields = ['nome', 'cognome', 'data_nascita', 'codice_fiscale',
                  'comune_nascita', 'provincia_nascita', 'stato_nascita',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza', 'stato_residenza',
                  'cap_residenza', 'email_contatto', 'iv', 'cm',
                  'note',]

    def __init__(self, *args, **kwargs):
        super(ModuloProfiloModificaAnagrafica, self).__init__(*args, **kwargs)
        #self.fields['note'].widget = forms.Textarea


class ModuloProfiloTitoloPersonale(autocomplete_light.ModelForm):

    OBBLIGATORIO = "Questo campo è obbligatorio per questo titolo."

    class Meta:
        model = TitoloPersonale
        fields = ['titolo', 'data_ottenimento', 'luogo_ottenimento',
                  'data_scadenza', 'codice',]

    def clean_data_ottenimento(self):
        titolo = self.cleaned_data['titolo']
        data_ottenimento = self.cleaned_data['data_ottenimento']
        if titolo.richiede_data_ottenimento and not data_ottenimento:
            raise ValidationError(self.OBBLIGATORIO)
        return data_ottenimento

    def clean_luogo_ottenimento(self):
        titolo = self.cleaned_data['titolo']
        luogo_ottenimento = self.cleaned_data['luogo_ottenimento']
        if titolo.richiede_luogo_ottenimento and not luogo_ottenimento:
            raise ValidationError(self.OBBLIGATORIO)
        return luogo_ottenimento

    def clean_data_scadenza(self):
        titolo = self.cleaned_data['titolo']
        data_scadenza = self.cleaned_data['data_scadenza']
        if titolo.richiede_data_ottenimento and not data_scadenza:
            raise ValidationError(self.OBBLIGATORIO)
        return data_scadenza

    def clean_codice(self):
        titolo = self.cleaned_data['titolo']
        codice = self.cleaned_data['codice']
        if titolo.richiede_data_ottenimento and not codice:
            raise ValidationError(self.OBBLIGATORIO)
        return codice


class ModuloModificaAvatar(ModelForm):
    class Meta:
        model = Persona
        fields = ['avatar']


class ModuloModificaPrivacy(ModelForm):
    class Meta:
        model = Persona
        fields = ['privacy_contatti', 'privacy_curriculum',
                  'privacy_deleghe', ]


class ModuloNuovaFototessera(ModelForm):
    class Meta:
        model = Fototessera
        fields = ['file']


class ModuloCreazioneDocumento(ModelForm):
    class Meta:
        model = Documento
        fields = ['tipo', 'file']


class ModuloModificaPassword(PasswordChangeForm):
    pass


class ModuloModificaEmailAccesso(ModelForm):
    class Meta:
        model = Utenza
        fields = ['email']


class ModuloModificaEmailContatto(ModelForm):
    class Meta:
        model = Persona
        fields = ['email_contatto']


class ModuloCreazioneTelefono(forms.Form):
    PERSONALE = "P"
    SERVIZIO = "S"
    TIPOLOGIA = (
        (PERSONALE, "Personale"),
        (SERVIZIO, "Di Servizio")
    )
    numero_di_telefono = forms.CharField(max_length=16, initial="+39 ")
    tipologia = forms.ChoiceField(choices=TIPOLOGIA, initial=PERSONALE, widget=forms.RadioSelect())


class ModuloCreazioneEstensione(autocomplete_light.ModelForm):
    class Meta:
        model = Estensione
        fields = ['destinazione', 'motivo']


class ModuloConsentiEstensione(forms.Form):
    protocollo_numero = forms.IntegerField(label="Numero di protocollo", help_text="Numero di protocollo con cui è stata registrata la richiesta.")
    protocollo_data = forms.DateField(label="Data del protocollo", help_text="Data di registrazione del protocollo.")


class ModuloCreazioneTrasferimento(autocomplete_light.ModelForm):
    class Meta:
        model = Trasferimento
        fields = ['destinazione', 'motivo']


class ModuloConsentiTrasferimento(forms.Form):
    protocollo_numero = forms.IntegerField(label="Numero di protocollo", help_text="Numero di protocollo con cui è stata registrata la richiesta.")
    protocollo_data = forms.DateField(label="Data del protocollo", help_text="Data di registrazione del protocollo.")


class ModuloNuovoProvvedimento(autocomplete_light.ModelForm):
    class Meta:
        model = ProvvedimentoDisciplinare
        fields = ['persona','sede', 'motivazione', 'tipo', 'inizio', 'fine', 'protocollo_data', 'protocollo_numero']

    def clean_fine(self):
        fine = self.cleaned_data['fine']
        inizio = self.cleaned_data['inizio']
        if not fine or fine < inizio:
            raise forms.ValidationError("La fine di un provvedimento non può avvenire prima del suo inizio")
        return fine


class ModuloCreazioneRiserva(ModelForm):
    class Meta:
        model = Riserva
        fields = ['inizio','fine', 'motivo']

    def clean_fine(self):
        fine = self.cleaned_data['fine']
        inizio = self.cleaned_data['inizio']
        if not fine or fine < inizio:
            raise forms.ValidationError("La fine di una riserva non può avvenire prima del suo inizio")
        return fine



class ModuloCreazioneDelega(autocomplete_light.ModelForm):
    class Meta:
        model = Delega
        fields = ['persona', ]

    def clean_inizio(self):  # Impedisce inizio passato
        inizio = self.cleaned_data['inizio']
        if inizio < datetime.date.today():
            raise forms.ValidationError("La data di inzio non può essere passata.")
        return inizio


class ModuloDonatore(autocomplete_light.ModelForm):
    class Meta:
        model = Donatore
        fields = ['gruppo_sanguigno', 'fattore_rh', 'fanotipo_rh',
                  'kell', 'codice_sit', 'sede_sit',]


class ModuloDonazione(autocomplete_light.ModelForm):
    class Meta:
        model = Donazione
        fields = ['sede', 'data', 'tipo',]


class ModuloUtenza(ModelForm):
    class Meta:
        model = Utenza
        fields = ['email',]


class ModuloPresidenteSede(ModelForm):
    class Meta:
        model = Sede
        fields = ['telefono', 'fax', 'email', 'codice_fiscale',
                  'partita_iva', ]
        