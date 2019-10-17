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

class ModuloServiziPrestazioni(forms.Form):
    @staticmethod
    def popola_previsioning():
        from attivita.cri_persone import getPrevisioning
        select = []
        prevision = getPrevisioning()

        if 'data' in prevision and 'generic_issue' in prevision['data']:
            for s in prevision['data']['generic_issue']:
                select.append(
                    (s['key'], s['summary'])
                )
        return tuple(select)

    provisioning = forms.MultipleChoiceField(
        required=False,
        choices=(),
        widget=forms.SelectMultiple,
        label="Approvvigionamenti"
    )


class ModuloServiziContatti(forms.Form):
    CRI = 'CRI'
    ALTRO_ENTE = 'ALTRO_ENTE'
    TIPO_CONTATTO = (
        ('', ''),
        (CRI, 'CRI'),
        (ALTRO_ENTE, 'Altro ente')
    )

    tipo_contatto = forms.ChoiceField(required=True, choices=TIPO_CONTATTO, label='Tipo Contatto')
    nome = forms.CharField(required=True, label='Nome')
    telefono = forms.CharField(required=False, label='Telefono')
    email = forms.CharField(required=False, label='Email')

class ModuloServiziConvenzioni(forms.Form):

    manage_progect = forms.ChoiceField(required=True, choices=(), label='Tipo Contatto')
    file = forms.FileField()


class ModuloServiziSepcificheDelServizio(forms.Form):
    MENSILE = 'Mensile'
    DA_A = 'Da - A'
    ACTIVATION_TYPE = (
        ('', ''),
        (MENSILE, 'Mensile'),
        (DA_A, 'Da a')
    )
    activationPeriodType = forms.ChoiceField(required=False, choices=ACTIVATION_TYPE, label='Periodo di attivazione')
    GENNAIO = 'Gennaio'
    FEBBRAIO = 'Febbraio'
    MARZO = 'Marzo'
    APRILE = 'Aprile'
    MAGGIO = 'Maggio'
    GIUGNO = 'Giugno'
    LUGLIO = 'Luglio'
    AGOSTO = 'Agosto'
    SETTEMPRE = 'Settembre'
    OTTOBRE = 'Ottobre'
    NOVEMBRE = 'Novembre'
    DICEMBRE = 'Dicembre'
    ANNUAL_PERIOD = (
        (GENNAIO, 'Gennaio'),
        (FEBBRAIO, 'Febbraio'),
        (MARZO, 'Marzo'),
        (APRILE, 'Aprile'),
        (MAGGIO, 'Maggio'),
        (GIUGNO, 'Giugno'),
        (LUGLIO, 'Luglio'),
        (AGOSTO, 'Agosto'),
        (SETTEMPRE, 'Settembre'),
        (OTTOBRE, 'Ottobre'),
        (NOVEMBRE, 'Novembre'),
        (DICEMBRE, 'Dicembre'),
    )
    annualPeriod = forms.MultipleChoiceField(
        choices=ANNUAL_PERIOD,
        label="Periodo",
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    annualPeriodFrom = forms.DateField(required=False, label='Da')
    annualPeriodTo = forms.DateField(required=False, label='A')

    SI = 'SI'
    NO = 'NO'
    SI_NO = (
        ('', ''),
        (SI, 'Si'),
        (NO, 'No'),
    )
    variableDay = forms.ChoiceField(required=False, choices=SI_NO, label='Variabile')

    # Todo: manca la chiamata
    costField = forms.CharField(required=False, label='Dati di costo (campo libero)')

    # Todo: manca la chiamata
    accessMode = forms.CharField(widget=forms.Textarea, required=False, label='Modailità di accesso')

    dueDate = forms.DateField(required=False, label='Chiusura')


class ModuloServiziSepcificheDelServizioTurni(forms.Form):

    H24 = 'H24'
    GIORNI_ORARI = 'Giorni e Orari'

    DAY_HOUR_TYPE = (
        ('', ''),
        (H24, 'H24'),
        (GIORNI_ORARI, 'Giorni e Orari')
    )
    dayHourType = forms.ChoiceField(required=False, choices=DAY_HOUR_TYPE, label='Orari')

    LUNEDI = 'LUNEDI'
    MARTEDI = 'MARTEDI'
    MERCOLEDI = 'MERCOLEDI'
    GIOVEDI = 'GIOVEDI'
    VENERDI = 'VENERDI'
    SABATO = 'SABATO'
    DOMENICA = 'DOMENICA'

    DAY = (
        ('', ''),
        (LUNEDI, 'Lunedi'),
        (MARTEDI, 'Martedi'),
        (MERCOLEDI, 'Mercoledi'),
        (GIOVEDI, 'Giovedi'),
        (VENERDI, 'Venerdi'),
        (SABATO, 'Sabato'),
        (DOMENICA, 'Domenica'),
    )

    giorno = forms.ChoiceField(required=False, choices=DAY, label='Giorno')
    orario_apertura = forms.CharField(required=False, label='Orario apertura')
    orario_chiusura = forms.CharField(required=False, label='Orario chiusura')


class ModuloServiziCriteriDiAccesso(forms.Form):
    COMUNI = 'Comuni'
    AMBITO_TERRITORIALE = 'Ambito Territoriale del Comitato'
    PROVINCIA = 'Provincia'
    REGIONALE = 'Regione'
    ITALIA = 'Italia'
    EUROPA = 'Europa'
    MONDO = 'Mondo'

    GEO_SCOPE = (
        ('', ''),
        (COMUNI, 'Comuni'),
        (AMBITO_TERRITORIALE, 'Ambito territoriale del comitato'),
        (PROVINCIA, 'Provincia'),
        (REGIONALE, 'Regione'),
        (ITALIA, 'Italia'),
        (EUROPA, 'Europa'),
        (MONDO, 'Mondo'),
    )
    R_BENEFICIARIES = (
        ('', ''),
        (AMBITO_TERRITORIALE, 'Ambito Territoriale del Comitato'),
        (COMUNI, 'Comuni')
    )
    address = forms.CharField(required=False, label='Indirizzo')
    geo_scope = forms.ChoiceField(required=False, choices=GEO_SCOPE, label='Ambito geografico')
    beneficiaries = forms.MultipleChoiceField(
        required=False,
        choices=(),
        widget=forms.SelectMultiple,
        label="Beneficiari"
    )
    eta_form = forms.IntegerField(required=False, label='Età Da')
    eta_to = forms.IntegerField(required=False, label='A')
    recidence_beneficiaries = forms.ChoiceField(required=False, choices=R_BENEFICIARIES, label='Residenza Beneficiari')
    beneficiaryMaxIsee = forms.CharField(required=False, label='Isee Max')
    otherBeneficiaryData = forms.CharField(widget=forms.Textarea, required=False, label='Beneficiari Altro')

    @staticmethod
    def popola_beneficiaries():
        from attivita.cri_persone import getBeneficiary
        select = []
        beneficiaries = getBeneficiary()
        if 'data' in beneficiaries and 'generic_issue' in beneficiaries['data']:
            for s in beneficiaries['data']['generic_issue']:
                select.append(
                    (s['key'], s['summary'])
                )
        return tuple(select)

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
