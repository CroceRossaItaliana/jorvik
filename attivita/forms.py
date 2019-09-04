import autocomplete_light
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.extras import SelectDateWidget
from attivita.cri_persone import getServiziStandard
from anagrafica.models import Sede
from attivita.models import Attivita, Turno, Area
from base.wysiwyg import WYSIWYGSemplice


class ModuloStoricoTurni(forms.Form):

    anni = (2000,)

    anno = forms.DateField(widget=SelectDateWidget(years=anni))


class ModuloAttivitaInformazioni(ModelForm):
    class Meta:
        model = Attivita
        fields = ['stato', 'apertura', 'estensione', 'descrizione', 'centrale_operativa']
        widgets = {
            "descrizione": WYSIWYGSemplice(),
        }


class ModuloServizioModifica(forms.Form):

    BOZZA = "11301"
    APERTA = "10413"
    CHIUSA = "6"
    choise = (
        (BOZZA, 'Bozza'),
        (APERTA, 'Aperta'),
        (CHIUSA, 'Chiusa')
    )
    stato = forms.ChoiceField(
        choices=choise, required=True, initial=BOZZA
    )

    testo = forms.CharField(required=False, max_length=100000, widget=forms.Textarea())


class ModuloServiziModificaStandard(forms.Form):

    @staticmethod
    def popola_scelta():
        select = []
        serviziStandard = getServiziStandard()
        if 'data' in serviziStandard and 'services' in serviziStandard['data']:
            for s in getServiziStandard()['data']['services']:
                select.append(
                    (s['key'], s['summary'])
                )
        return tuple(select)

    servizi = forms.MultipleChoiceField(
        choices=(),
        widget=forms.SelectMultiple,
        label="Scelta servizi standard"
    )


class ModuloModificaTurno(ModelForm):
    class Meta:
        model = Turno
        fields = ['nome', 'inizio', 'fine', 'minimo', 'massimo', 'prenotazione']

    def clean(self):
        try:
            fine = self.cleaned_data['fine']
            inizio = self.cleaned_data['inizio']
            minimo = self.cleaned_data['minimo']
            massimo = self.cleaned_data['massimo']
            prenotazione = self.cleaned_data['prenotazione']

        except KeyError:
            raise ValidationError("Compila correttamente tutti i campi.")

        if fine <= inizio:
            self.add_error("fine", "L'orario di fine turno deve essere successivo "
                                   "all'orario di inzio.")

        if prenotazione > fine:
            self.add_error("prenotazione",  "L'orario entro il quale prenotarsi deve essere "
                                            "precedente alla fine del turno. ")

        if minimo < 0:
            self.add_error("minimo", "Inserisci un numero positivo.")

        if massimo and minimo > massimo:
            self.add_error("massimo", "Il massimo deve essere maggiore del minimo.")


class ModuloCreazioneTurno(ModuloModificaTurno):
    pass


class ModuloAggiungiPartecipanti(forms.Form):
    persone = autocomplete_light.forms.ModelMultipleChoiceField("PersonaAutocompletamento",
                                                                help_text="Seleziona uno o più persone da "
                                                                          "aggiungere come partecipanti.")


class FiltroAreaProgetto(forms.Form):

    SCELTE = (
        ('T', 'Tutto'),
        ('A', 'Aree'),
        ('P', 'Progetti')
    )

    scelta = forms.ChoiceField(choices=SCELTE, required=True)


class ModuloOrganizzaServizio(forms.Form):

    @staticmethod
    def popola_scelta():
        select = []
        serviziStandard = getServiziStandard()
        if 'data' in serviziStandard and 'services' in serviziStandard['data']:
            for s in getServiziStandard()['data']['services']:
                select.append(
                    (s['key'], s['summary'])
                )
        return tuple(select)

    @staticmethod
    def popola_progetto(me):
        from attivita.models import Progetto
        from anagrafica.permessi.costanti import GESTIONE_ATTIVITA_SEDE
        select = [('', 'Seleziona un progetto')]
        qs = Progetto.objects.filter(
            sede__in=me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE, solo_deleghe_attive=True)
        )
        for p in qs:
            select.append(
                (p.nome, p.nome)
        )
        return tuple(select)

    progetto = forms.ChoiceField()
    servizi = forms.MultipleChoiceField(
        choices=(),
        widget=forms.SelectMultiple,
        label="Scelta servizi standard"
    )


class ModuloCreazioneArea(ModelForm):

    progetto = forms.BooleanField(
        initial=False,
        label='Se spunti questo flag a questo Progetto potrai collegare i servizi offerti alla Popolazione.',
        required=False
    )

    class Meta:
        model = Area
        fields = ['nome', 'obiettivo',]


class ModuloOrganizzaAttivita(ModelForm):

    gruppo = forms.BooleanField(required=False, initial=False, label="Vuoi creare un gruppo di lavoro per quest'attività?")
    class Meta:
        model = Attivita
        fields = ['nome', 'area', ]


class ModuloOrganizzaAttivitaReferente(forms.Form):

    SONO_IO = "IO"
    SCEGLI_REFERENTI = "SC"
    SCELTA = (
        (None,  "-- Scegli un'opzione --"),
        (SONO_IO, "Sarò io il referente per questa attività"),
        (SCEGLI_REFERENTI, "Fammi scegliere uno o più referenti che gestiranno "
                           "quest'attività")
    )

    @staticmethod
    def popola_scelta():
        from attivita.models import NonSonoUnBersaglio
        bersaglio = NonSonoUnBersaglio.objects.all()
        choices = [
            (None,  "-- Scegli un'opzione --"),
            (ModuloOrganizzaAttivitaReferente.SONO_IO, "Sarò io il referente per questa attività"),
            (ModuloOrganizzaAttivitaReferente.SCEGLI_REFERENTI, "Fammi scegliere uno o più referenti che gestiranno "
                               "quest'attività"),
        ]
        for b in bersaglio:
            choices.append((b.persona.id, b.persona))

        return choices

    scelta = forms.ChoiceField(
        choices=SCELTA,
        help_text="Scegli l'opzione appropriata."
    )


class ModuloStatisticheAttivita(forms.Form):

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


class ModuloStatisticheAttivitaPersona(forms.Form):

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


class ModuloRipetiTurno(forms.Form):

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
