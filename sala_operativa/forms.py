from autocomplete_light import shortcuts as autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form
from django import forms
from django.forms.extras import SelectDateWidget
from django.utils import timezone
from django.utils.timezone import now

from anagrafica.costanti import LOCALE
from anagrafica.models import Sede
from anagrafica.permessi.costanti import GESTIONE_SO_SEDE
from base.wysiwyg import WYSIWYGSemplice
from .models import ServizioSO, TurnoSO, ReperibilitaSO, MezzoSO, PrenotazioneMMSO, DatoreLavoro, OperazioneSO, \
    FunzioneSO


class VolontarioReperibilitaForm(Form):

    estensione = forms.MultipleChoiceField(
        label="Estensione di reperibiltà",
        widget=forms.CheckboxSelectMultiple,
        choices=ReperibilitaSO.ESTENSIONE_CHOICES
    )
    inizio = forms.DateTimeField()
    fine = forms.DateTimeField()
    attivazione = forms.TimeField(initial='00:15')
    applicazione_bdl = forms.BooleanField(label="Applicazione dei Benefici di Legge", required=False)
    datore_lavoro = forms.ChoiceField(choices=(), required=False)

    def clean(self):
        cd = self.cleaned_data

        if cd['applicazione_bdl'] and cd['datore_lavoro'] == '0':
            self.add_error('datore_lavoro', 'Se vengono applicati i benefici di legge, devi inserire il datore di lavoro.')

        return cd

    @staticmethod
    def popola_datore(persona):
        l = [
            ('0', '--------')
        ]
        for datore in DatoreLavoro.objects.filter(persona=persona):
            l.append(
                (datore.pk, datore.nominativo)
            )
        return l


class VolontarioReperibilitaModelForm(ModelForm):
    # datore_lavoro = forms.ChoiceField(choices=(), required=False)

    class Meta:
        model = ReperibilitaSO
        fields = ['estensione', 'inizio', 'fine', 'attivazione',
                  'applicazione_bdl', 'datore_lavoro']


# class AggiungiReperibilitaPerVolontarioForm(ModelForm):
#     persona = autocomplete_light.ModelChoiceField("AggiungiReperibilitaPerVolontario", )
#
#     class Meta:
#         model = ReperibilitaSO
#         fields = ['persona', 'estensione', 'inizio', 'fine', 'attivazione',
#                   'applicazione_bdl', ]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


class AggiungiReperibilitaPerVolontarioForm(Form):
    persona = autocomplete_light.ModelChoiceField("AggiungiReperibilitaPerVolontario", )

    estensione = forms.MultipleChoiceField(
        label="Estensione di reperibiltà",
        widget=forms.CheckboxSelectMultiple,
        choices=ReperibilitaSO.ESTENSIONE_CHOICES
    )
    inizio = forms.DateTimeField()
    fine = forms.DateTimeField()
    attivazione = forms.TimeField(initial='00:15')
    applicazione_bdl = forms.BooleanField(label="Applicazione dei Benefici di Legge", required=False)
    datore_lavoro = forms.ChoiceField(choices=(), required=False)

    def clean(self):
        cd = self.cleaned_data

        if cd['applicazione_bdl'] and cd['datore_lavoro'] == '0':
            self.add_error('datore_lavoro', 'Se vengono applicati i benefici di legge, devi inserire il datore di lavoro.')

        return cd

    @staticmethod
    def popola_datore(persona):
        l = [
            ('0', '--------')
        ]
        for datore in DatoreLavoro.objects.filter(creat=persona):
            l.append(
                (datore.pk, datore.nominativo)
            )
        return l


class ModuloProfiloModificaAnagraficaDatoreLavoro(ModelForm):
    class Meta:
        model = DatoreLavoro
        fields = ['nominativo', 'ragione_sociale', 'partita_iva',
                  'telefono', 'referente',
                  'email', 'pec']


class StoricoTurniForm(forms.Form):
    anni = (2000,)
    anno = forms.DateField(widget=SelectDateWidget(years=anni))


class ModificaServizioForm(ModelForm):
    class Meta:
        model = ServizioSO
        fields = ['stato', 'apertura', 'estensione', 'impiego_bdl', 'descrizione', ]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }

    def __init__(self, *args, **kwargs):
        self.servizio = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if self.servizio.estensione.estensione == LOCALE:
            self.fields['stato'].widget.attrs['readonly'] = True


class ModificaTurnoForm(ModelForm):
    class Meta:
        model = TurnoSO
        fields = ['nome', 'inizio', 'fine', 'minimo', 'massimo', ]

    def clean(self):
        try:
            cd = self.cleaned_data
            fine, inizio = cd['fine'], cd['inizio']
            minimo, massimo = cd['minimo'], cd['massimo']
        except KeyError as e:
            raise ValidationError("Compila correttamente tutti i campi.")

        if fine <= inizio:
            self.add_error("fine", "L'orario di fine turno deve essere successivo all'orario di inzio.")

        if minimo < 0:
            self.add_error("minimo", "Inserisci un numero positivo.")

        if massimo and minimo > massimo:
            self.add_error("massimo", "Il massimo deve essere maggiore del minimo.")

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance and instance.passato:
            keys = self.fields.keys()
            for k in keys:
                self.fields[k].widget.attrs['readonly'] = True



class CreazioneTurnoForm(ModificaTurnoForm):
    pass


class AggiungiPartecipantiForm(forms.Form):
    persone = autocomplete_light.ModelMultipleChoiceField('TrovaReperibilitaPerTurno',
        help_text="Seleziona uno o più persone da aggiungere come partecipanti.")


class OrganizzaServizioForm(ModelForm):
    servizi_standard_CHOICES = ServizioSO.servizi_standard()

    servizi_standard = forms.ChoiceField(
        required=False,
        choices=[(None, '--------')] + servizi_standard_CHOICES,
        help_text='Scegli un nome predefinito o dai il nome al servizio nel '
                  'campo "Nome" che si trova sotto',
    )

    def clean(self):
        cd = self.cleaned_data
        servizi_standard, nome = cd['servizi_standard'], cd['nome']
        if servizi_standard and nome:
            self.add_error('nome', 'Uno dei campi "Nome" devono rimanere non valorizzati.')

        if servizi_standard and not nome:
            cd['nome'] = dict(self.servizi_standard_CHOICES)[servizi_standard]

    class Meta:
        model = ServizioSO
        fields = ['funzione', 'servizi_standard', 'nome', 'sede', 'inizio', 'fine',
                  'impiego_bdl', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servizi_standard'].label = 'Attività'
        self.fields['impiego_bdl'].help_text = 'Le attività in Convenzione o non legate all’emergenza in corso non possono prevedere l’attivazione dei Benefici di Legge (art. 39 e 40 del dlgs 1/2018)"'

        self.fields['nome'].initial = ''
        self.fields['nome'].required = False
        self.fields['nome'].widget = forms.TextInput(attrs={})  # to override required attr


class OrganizzaOperazioneForm(ModelForm):
    class Meta:
        model = OperazioneSO
        fields = ["nome", "archivia_emergenza", "impiego_bdl", "attivatore", "funzioni", "inizio", "fine", "operazione", "comitato", "sede", "sede_internazionale"]


class OrganizzaFunzioneForm(ModelForm):
    class Meta:
        model = FunzioneSO
        fields = ["nome", "settore"]


class OrganizzaServizioReferenteForm(forms.Form):
    SONO_IO = "IO"
    SCEGLI_REFERENTI = "SC"
    SCELTA = (
        (None, "-- Scegli un'opzione --"),
        (SONO_IO, "Sarò io il referente per questa attività"),
        (SCEGLI_REFERENTI, "Fammi scegliere uno o più referenti che gestiranno "
                           "quest'attività")
    )

    scelta = forms.ChoiceField(
        choices=SCELTA,
        help_text="Scegli l'opzione appropriata."
    )


class OrganizzaOperazioneReferenteForm(forms.Form):
    SONO_IO = "IO"
    SCEGLI_REFERENTI = "SC"
    SCELTA = (
        (None, "-- Scegli un'opzione --"),
        (SONO_IO, "Sarò io il referente per questa attività"),
        (SCEGLI_REFERENTI, "Fammi scegliere uno o più referenti che gestiranno "
                           "quest'attività")
    )

    scelta = forms.ChoiceField(
        choices=SCELTA,
        help_text="Scegli l'opzione appropriata."
    )

class OrganizzaFunzioneReferenteForm(forms.Form):
    SONO_IO = "IO"
    SCEGLI_REFERENTI = "SC"
    SCELTA = (
        (None, "-- Scegli un'opzione --"),
        (SONO_IO, "Sarò io il referente per questa attività"),
        (SCEGLI_REFERENTI, "Fammi scegliere uno o più referenti che gestiranno "
                           "quest'attività")
    )

    scelta = forms.ChoiceField(
        choices=SCELTA,
        help_text="Scegli l'opzione appropriata."
    )

class RipetiTurnoForm(forms.Form):
    # Giorni della settimana numerici, come
    #  da datetime.weekday()
    LUNEDI = 0
    MARTEDI = 1
    MERCOLEDI = 2
    GIOVEDI = 3
    VENERDI = 4
    SABATO = 5
    DOMENICA = 6
    GIORNI = (
        (LUNEDI, "Lunedì"),
        (MARTEDI, "Martedì"),
        (MERCOLEDI, "Mercoledì"),
        (GIOVEDI, "Giovedì"),
        (VENERDI, "Venerdì"),
        (SABATO, "Sabato"),
        (DOMENICA, "Domenica")
    )

    TUTTI = (LUNEDI, MARTEDI, MERCOLEDI, GIOVEDI, VENERDI, SABATO, DOMENICA)

    giorni = forms.MultipleChoiceField(choices=GIORNI, initial=TUTTI, required=True,
                                       help_text="In quali giorni della settimana si svolgerà "
                                                 "questo turno? Tieni premuto CTRL per selezionare "
                                                 "più giorni. ")

    numero_ripetizioni = forms.IntegerField(min_value=1, max_value=60, initial=3,
                                            help_text="Per quanti giorni vuoi ripetere questo turno? ")


class CreazioneMezzoSO(ModelForm):

    def clean(self):
        cd = self.cleaned_data
        tipo = cd.get('tipo')
        mezzo_tipo = cd.get('mezzo_tipo')

        if tipo and mezzo_tipo and (tipo != MezzoSO.MEZZO and tipo != MezzoSO.MEZZO_PRIVATO):
            self.add_error('mezzo_tipo', 'Il tipo del mezzo è selezionabile solo con tipo "Mezzo".')
        return cd

    class Meta:
        model = MezzoSO
        fields = ['nome', 'tipo', 'mezzo_tipo', 'targa', 'modello', 'estensione', 'stato']


class AbbinaMezzoMaterialeForm(ModelForm):
    class Meta:
        model = PrenotazioneMMSO
        fields = ["inizio", "fine", ]

    def clean_inizio(self):
        inizio = self.cleaned_data['inizio']
        if inizio < now() - timezone.timedelta(minutes=5):
            raise ValidationError('Non puoi abbinare il mezzo o materiale con la data di inizio già passata.')
        return inizio

    def clean_fine(self):
        fine = self.cleaned_data['fine']
        if fine < now():
            raise ValidationError('Non puoi abbinare il mezzo o materiale con la data di fine già passata.')
        return fine

    def clean(self):
        mezzo = self.instance

        cd = self.cleaned_data
        inizio, fine = cd.get("inizio"), cd.get("fine")

        occupato = PrenotazioneMMSO.occupazione_nel_range(mezzo, inizio, fine)
        if occupato:
            message = """L'orario selezionato non è disponibile. 
            Questo %s è stato già prenotato per uno dei servizi attivi.""" % \
                      mezzo.get_tipo_display().lower()
            self.add_error("fine", message)

        return cd


class StatisticheServiziForm(forms.Form):
    SETTIMANA = 7
    QUINDICI_GIORNI = 15
    MESE = 30
    SCELTE = (
        (SETTIMANA, "Per settimana"),
        (QUINDICI_GIORNI, "Per 15 giorni"),
        (MESE, "Per mese"),
    )

    sedi = forms.ModelMultipleChoiceField(queryset=Sede.objects.filter(attiva=True))
    periodo = forms.ChoiceField(choices=SCELTE, initial=SETTIMANA)
