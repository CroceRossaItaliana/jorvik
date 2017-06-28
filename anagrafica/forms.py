import datetime
import unicodecsv
import stdnum
from dateutil.parser import parse

from django import forms
from django.conf import settings
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from anagrafica.models import Sede, Persona, Appartenenza, Documento, Estensione, ProvvedimentoDisciplinare, Delega, \
    Fototessera, Trasferimento, Riserva
from anagrafica.validators import valida_almeno_14_anni
from autenticazione.models import Utenza
from autocomplete_light import shortcuts as autocomplete_light

from base.forms import ModuloMotivoNegazione
from curriculum.models import TitoloPersonale
from sangue.models import Donatore, Donazione


class ModuloSpostaPersone(object):

    def elenco_persone(self, source):
        return source, []

    def mappa_persone(self, source):
        return source, []

    def sposta_persone(self, firmatario, source=None, persone=None):
        trasferimenti = []
        if source and not persone:
            persone, errori = self.elenco_persone(source)
        if not persone:
            persone = []
        for persona in persone:
            if persona['sede']:
                trasferita = persona['persona'].trasferimento_massivo(
                    persona['sede'],
                    firmatario,
                    persona['motivazione'],
                    persona['inizio_appartenenza']
                )
                trasferimenti.append((persona['persona'], trasferita))
            else:
                trasferimenti.append((persona['persona'], 'Non è stata specificata la sede'))

        return trasferimenti


class ModuloSpostaPersoneManuale(ModuloSpostaPersone, forms.Form):
    sede = autocomplete_light.ModelChoiceField("SedeAutocompletamento")
    inizio_appartenenza = forms.DateField(label='Data di inizio appartenenza', widget=AdminDateWidget(format='%Y-%m-%d'))
    motivazione = forms.CharField()

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'core.js',
            'vendor/jquery/jquery%s.js' % extra,
            'jquery.init.js',
            'admin/RelatedObjectLookups.js',
        ]
        return forms.Media(js=[static('admin/js/%s' % url) for url in js]) + super(ModuloSpostaPersone, self).media

    def mappa_persone(self, source):
        trasferimenti = []
        for persona in source.order_by('cognome', 'nome'):
            trasferimenti.append({
                'persona': persona,
                'sede': self.cleaned_data['sede'],
                'motivazione': self.cleaned_data['motivazione'],
                'inizio_appartenenza': self.cleaned_data['inizio_appartenenza']
            })
        return trasferimenti, []


class ModuloSpostaPersoneDaCSV(ModuloSpostaPersone, forms.Form):
    dati = forms.FileField(
        required=False, help_text=mark_safe(
            'Il file deve essere in formato CSV, con i seguenti campi: '
            '<pre>CF,DATA INIZIO APPARTENENZA (AAAA-MM-GG),ID NUOVA SEDE,MOTIVAZIONE,</pre>'
        )
    )
    procedi = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def elenco_persone(self, source):
        dati = {}
        sedi = set()
        trasferimenti = []
        scarti = []
        if self.is_valid():
            data = unicodecsv.reader(source)
            for persona in data:
                dati[persona[0]] = persona
                try:
                    sedi.add(int(persona[2]))
                except ValueError:
                    scarti.append(persona[0])
            sedi = {str(sede.pk): sede for sede in Sede.objects.filter(pk__in=sedi)}
            for persona in Persona.objects.filter(codice_fiscale__in=dati.keys()).order_by('cognome', 'nome'):
                dati_persona = dati[persona.codice_fiscale]
                sede = sedi.get(dati_persona[2], None)
                try:
                    data = parse(dati_persona[1])
                    trasferimenti.append({
                        'persona': persona,
                        'sede': sede,
                        'motivazione': dati_persona[3],
                        'inizio_appartenenza': data,
                    })
                except (ValueError, OverflowError, KeyError):
                    scarti.append(persona.codice_fiscale)
        return trasferimenti, scarti


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
        codice_fiscale = codice_fiscale.upper()
        return codice_fiscale

    def clean_data_nascita(self):
        data_nascita = self.cleaned_data.get('data_nascita')
        valida_almeno_14_anni(data_nascita)
        return data_nascita


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
    destinazione = autocomplete_light.ModelChoiceField("SedeTrasferimentoAutocompletamento", error_messages={
        'invalid': "Non è possibile effettuare un trasferimento verso il Comitato Nazionale, verso i Comitati Regionali"
                   "e verso i comitati delle Province Autonome di Trento e Bolzano"
    })

    class Meta:
        model = Estensione
        fields = ['destinazione', 'motivo']


class ModuloConsentiEstensione(forms.Form):
    protocollo_numero = forms.CharField(max_length=32, label="Numero di protocollo", help_text="Numero di protocollo con cui è stata registrata la richiesta.")
    protocollo_data = forms.DateField(label="Data del protocollo", help_text="Data di registrazione del protocollo.")


class ModuloNegaEstensione(ModuloMotivoNegazione):
    pass


class ModuloCreazioneTrasferimento(autocomplete_light.ModelForm):
    destinazione = autocomplete_light.ModelChoiceField("SedeTrasferimentoAutocompletamento", error_messages={
        'invalid': "Non è possibile effettuare un trasferimento verso il Comitato Nazionale, verso i Comitati Regionali"
                   "e verso i comitati delle Province Autonome di Trento e Bolzano"
    })

    class Meta:
        model = Trasferimento
        fields = ['destinazione', 'motivo']


class ModuloConsentiTrasferimento(forms.Form):
    protocollo_numero = forms.CharField(max_length=32, label="Numero di protocollo", help_text="Numero di protocollo con cui è stata registrata la richiesta.")
    protocollo_data = forms.DateField(label="Data del protocollo", help_text="Data di registrazione del protocollo.")


class ModuloConsentiRiserva(ModuloConsentiTrasferimento):
    pass


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
        inizio = self.cleaned_data.get('inizio', None)
        if inizio and (not fine or fine < inizio):
            raise forms.ValidationError("La fine di una riserva non può avvenire prima del suo inizio")
        return fine

    def clean_inizio(self):
        inizio = self.cleaned_data['inizio']
        if inizio < now():
            raise forms.ValidationError("Non può essere richiesta una riserva per una data nel passato")
        return inizio


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
        fields = ['gruppo_sanguigno', 'fattore_rh', 'fenotipo_rh',
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
        fields = ['telefono', 'fax', 'email', 'pec',
                  'sito_web', 'iban',
                  'codice_fiscale', 'partita_iva', ]

    def clean_partita_iva(self):
        partita_iva = self.cleaned_data['partita_iva']
        return stdnum.it.iva.compact(partita_iva)

    def clean(self):
        # Tutti i campi obbligatori
        campi_obbligatori = ['telefono', 'email', 'pec', 'iban', 'codice_fiscale', 'partita_iva']
        tutti_campi = {y: v for y, v in self.cleaned_data.copy().items() if y in campi_obbligatori}.items()
        for chiave, valore in tutti_campi:
            if not valore:
                self.add_error(chiave, "Questo campo è obbligatorio.")


class ModuloImportVolontari(forms.Form):
    file_csv = forms.FileField()

    VALIDA = "V"
    IMPORTA = "I"
    SCELTE = (
        (VALIDA, "Valida solamente"),
        (IMPORTA, "Valida e importa le righe valide"),
    )
    azione = forms.ChoiceField(choices=SCELTE, initial=VALIDA)

    VIRGOLA = ','
    PUNTO_E_VIRGOLA = ';'
    DELIMITATORI = (
        (VIRGOLA, "Virgola"),
        (PUNTO_E_VIRGOLA, "Punto e virgola")
    )
    delimitatore = forms.ChoiceField(choices=DELIMITATORI, initial=VIRGOLA)


class ModuloModificaDataInizioAppartenenza(ModelForm):
    class Meta:
        model = Appartenenza
        fields = ['inizio', ]

    def clean_inizio(self):
        from django.utils import timezone
        inizio = self.cleaned_data['inizio']
        if inizio > timezone.now():
            raise ValidationError("La data non può essere nel futuro.")
        if self.instance and not self.instance.modificabile(inizio):
            raise ValidationError("La data non può sovrapporsi con appartenenze precedenti.")
        return inizio


class ModuloImportPresidenti(forms.Form):
    presidente = autocomplete_light.ModelChoiceField("PresidenteAutocompletamento")
    sede = autocomplete_light.ModelChoiceField("ComitatoAutocompletamento")


class ModuloPulisciEmail(forms.Form):
    indirizzi = forms.CharField(widget=forms.Textarea, help_text="Un indirizzo e-mail per riga.")


class ModuloUSModificaUtenza(ModuloUtenza):

    ok_1 = forms.BooleanField(label="La richiesta di modifica è pervenuta dall'utente stesso.",
                              required=False)
    ok_2 = forms.BooleanField(label="Ho già avvisato l'utente di questa modifica.",
                              required=False)
    ok_3 = forms.BooleanField(label="Sono consapevole che l'utente non potrà più entrare in Gaia "
                                    "con il vecchio indirizzo.")
    ok_4 = forms.BooleanField(label="Sono consapevole che l'e-mail deve essere corretta, per "
                                    "permettere all'utente di accedere a Gaia.")

    def clean(self):
        ok_1 = self.cleaned_data.get('ok_1')
        ok_2 = self.cleaned_data.get('ok_2')
        if not(ok_1 or ok_2):
            raise ValidationError("Puoi solo cambiare l'e-mail di accesso se questa è stata "
                                  "richiesta dall'utente, oppure hai già avvisato l'utente della "
                                  "modifica e della nuova e-mail per accedere.")
