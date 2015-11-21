from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import ModelForm
import mptt
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Estensione
from autenticazione.models import Utenza


class ModuloStepComitato(ModelForm):
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
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    # Effettua dei controlli personalizzati sui sui campi
    def clean(self):
        cleaned_data = self.cleaned_data

        # Fa il controllo di univocita' sull'indirizzo e-mail
        email = cleaned_data.get('email')
        if Utenza.objects.filter(email=email).exists():  # Esiste gia'?
            self._errors['email'] = self.error_class(['Questa e-mail esiste in Gaia.'])

        # TODO Controllo robustezza password

        return cleaned_data


class ModuloStepAnagrafica(ModelForm):
    class Meta:
        model = Persona
        fields = ['nome', 'cognome', 'data_nascita', 'comune_nascita', 'provincia_nascita', 'stato_nascita',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza', 'stato_residenza',
                  'cap_residenza']


class ModuloModificaAnagrafica(ModelForm):
    class Meta:
        model = Persona
        fields = ['data_nascita', 'comune_nascita', 'provincia_nascita', 'stato_nascita',
                  'indirizzo_residenza', 'comune_residenza', 'provincia_residenza', 'stato_residenza',
                  'cap_residenza']


class ModuloModificaAvatar(ModelForm):
    class Meta:
        model = Persona
        fields = ['avatar']


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


class ModuloCreazioneEstensione(ModelForm):
    class Meta:
        model = Estensione
        fields = ['destinazione']

class ModuloConsentiEstensione(ModelForm):
    protocollo_numero = forms.IntegerField(label="Numero di protocollo", help_text="Numero di protocollo con cui è stata accettata la richiesta")
    protocollo_data = forms.DateField(label="Data del protocollo", help_text="Data di registrazione del protocollo")

