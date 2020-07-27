from autocomplete_light import shortcuts as autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.extras import SelectDateWidget
from django.utils.timezone import now

from anagrafica.models import Sede
from anagrafica.permessi.costanti import GESTIONE_SO_SEDE
from base.wysiwyg import WYSIWYGSemplice
from .models import ServizioSO, TurnoSO, ReperibilitaSO, MezzoSO, PrenotazioneMMSO


class VolontarioReperibilitaForm(ModelForm):
    class Meta:
        model = ReperibilitaSO
        fields = ['estensione', 'inizio', 'fine', 'attivazione', ]


class AggiungiReperibilitaPerVolontarioForm(ModelForm):
    persona = autocomplete_light.ModelChoiceField("AggiungiReperibilitaPerVolontario", )

    class Meta:
        model = ReperibilitaSO
        fields = ['persona', 'estensione', 'inizio', 'fine', 'attivazione', ]


class StoricoTurniForm(forms.Form):
    anni = (2000,)
    anno = forms.DateField(widget=SelectDateWidget(years=anni))


class AttivitaInformazioniForm(ModelForm):
    class Meta:
        model = ServizioSO
        fields = ['stato', 'apertura', 'estensione', 'descrizione', ]
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }


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
            print(e)
            raise ValidationError("Compila correttamente tutti i campi.")

        if fine <= inizio:
            self.add_error("fine", "L'orario di fine turno deve essere successivo all'orario di inzio.")

        if minimo < 0:
            self.add_error("minimo", "Inserisci un numero positivo.")

        if massimo and minimo > massimo:
            self.add_error("massimo", "Il massimo deve essere maggiore del minimo.")


class CreazioneTurnoForm(ModificaTurnoForm):
    pass


class AggiungiPartecipantiForm(forms.Form):
    persone = autocomplete_light.ModelMultipleChoiceField("PersonaAutocompletamento",
                                                          help_text="Seleziona uno o più persone da "
                                                                    "aggiungere come partecipanti.")


class OrganizzaServizioForm(ModelForm):
    class Meta:
        model = ServizioSO
        fields = ['nome', 'sede', 'inizio', 'fine', ]


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


class StatisticheAttivitaForm(forms.Form):
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


class StatisticheAttivitaPersonaForm(forms.Form):
    SETTIMANA = 7
    QUINDICI_GIORNI = 15
    MESE = 30
    ANNO = 365
    SCELTE = (
        (SETTIMANA, "Per settimana"),
        (QUINDICI_GIORNI, "Per 15 giorni"),
        (MESE, "Per mese"),
        (ANNO, "Per anno"),
    )

    periodo = forms.ChoiceField(choices=SCELTE, initial=SETTIMANA)


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
    def clean_inizio(self):
        inizio = self.cleaned_data['inizio']
        if inizio < now():
            raise ValidationError('Non puoi creare il mezzo o materiale con la data di inizio già passata.')
        return inizio

    def clean_fine(self):
        fine = self.cleaned_data['fine']
        if fine < now():
            raise ValidationError('Non puoi creare il mezzo o materiale con la data di fine già passata.')
        return fine

    def clean(self):
        cd = self.cleaned_data
        tipo = cd.get('tipo')
        mezzo_tipo = cd.get('mezzo_tipo')

        if tipo and mezzo_tipo and tipo != MezzoSO.MEZZO:
            self.add_error('mezzo_tipo', 'Il tipo del mezzo è selezionabile solo con tipo "Mezzo".')
        return cd

    class Meta:
        model = MezzoSO
        fields = ['nome', 'tipo', 'mezzo_tipo', 'estensione', 'inizio', 'fine', ]


class AbbinaMezzoMaterialeForm(ModelForm):
    class Meta:
        model = PrenotazioneMMSO
        fields = ["inizio", "fine", ]

    def clean_inizio(self):
        inizio = self.cleaned_data['inizio']
        if inizio < now():
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
