import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, modelformset_factory

from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.permessi.applicazioni import DELEGATO_AREA, RESPONSABILE_AREA
from anagrafica.permessi.costanti import GESTIONE_SEDE
from django.utils.timezone import now

from base.wysiwyg import WYSIWYGSemplice

from anagrafica.permessi import applicazioni as permessi
from anagrafica.costanti import LOCALE, REGIONALE, NAZIONALE
from anagrafica.models import Delega, Appartenenza, Sede
from curriculum.models import Titolo
from curriculum.areas import OBBIETTIVI_STRATEGICI
from jorvik import settings
from .models import (Corso, CorsoBase, CorsoFile, CorsoEstensione,
                     LezioneCorsoBase, PartecipazioneCorsoBase, RelazioneCorso, Evento, EventoFile)


class ModuloCreazioneEvento(ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nome',
            'data_inizio',
            'data_fine',
            'sede',
            'descrizione'
        ]


class ModuloModificaEvento(ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nome',
            'data_inizio',
            'data_fine',
            'descrizione'
        ]

class FiltraEvento(ModelForm):
    class Meta:
        model = Evento
        fields = [
            'stato',
        ]

class ModuloCreazioneCorsoBase(ModelForm):
    PRESSO_SEDE = "PS"
    ALTROVE = "AL"
    ONLINE = "OL"
    LOCAZIONE = (
        (PRESSO_SEDE, "Il corso si svolgerà presso la Sede"),
        (ALTROVE, "Il corso si svolgerà altrove"),
        (ONLINE, "Modalità online"),
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
        from datetime import datetime
        start_date = datetime.strptime(settings.INIZIO_CRIOL_ATTIVABILE, '%m/%d/%Y %H:%M:%S')

        if tipo == 'BO' and start_date > datetime.now():
            self.add_error(
                'tipo',
                'Puoi creare questo corso dal {} '.format(
                    start_date.strftime("%m/%d/%Y alle %H:%M:%S")
                )
            )

        data_esame, data_inizio = cd.get('data_esame'), cd.get('data_inizio')

        if not data_esame:
            self.add_error('data_esame', 'Controllare la data di esame')

        if not data_inizio:
            self.add_error('data_inizio', 'Controllare la data di inizio')

        if data_esame < data_inizio:
            self.add_error('data_esame', "La data deve essere successiva alla data di inizio.")

        if tipo == Corso.BASE or tipo == Corso.BASE_ONLINE:
            # cd non può/deve avere valori per questi campi se corso è BASE
            for field in ['area', 'level', 'titolo_cri']:
                if field in cd:
                    del cd[field]

        if tipo == Corso.CORSO_NUOVO or tipo == Corso.CORSO_ONLINE or tipo == Corso.CORSO_EQUIPOLLENZA:
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
                  'delibera_file', 'sede', 'evento']
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
        delega = me.deleghe_attuali().filter(tipo__in=[permessi.COMMISSARIO,
                                                       permessi.PRESIDENTE,
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
    docente = autocomplete_light.ModelMultipleChoiceField("DocenteLezioniCorso", required=False)
    show_docente_esterno = forms.BooleanField(label="Hai docenti esterni?", initial=False, required=False)
    has_nulla_osta = forms.BooleanField(label='Responsabilità di aver ricevuto nulla osta dal presidente del comitato di appartenenza',
                                        initial=True)
    fine = forms.DateTimeField()
    obiettivo = forms.CharField(required=False, label='Argomento')

    @property
    def has_instance(self):
        return hasattr(self, 'instance')

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

        # Validazione divisione lezioni e orari impostati
        if self.has_instance and not self.instance.divisa:
            lezione_ore = self.instance.lezione_ore
            if lezione_ore:
                duration = fine.timestamp() - inizio.timestamp()

                # days, seconds = duration.days, duration.seconds
                # hours = days * 24 + seconds // 3600
                # hours = datetime.timedelta(hours=hours)

                if duration > lezione_ore.seconds and not self.corso.online and not self.corso.tipo == Corso.BASE_ONLINE:
                    self.add_error('fine', 'La durata della lezione non può essere '
                        'maggiore della durata impostata nella scheda per questa lezione (%s). '
                        'Hai indicato %s' % (lezione_ore, datetime.timedelta(seconds=duration)))

        self.clean_docente_fields()

        return cd

    def clean_docente_fields(self):
        cd = self.cleaned_data
        docente, docente_esterno = cd['docente'], cd['docente_esterno']

        if not docente and not docente_esterno:
            self.add_error('docente', 'Devi inserire almeno un docente')

    def clean_obiettivo(self):
        if self.has_instance:
            if self.instance.precaricata:  # non salvare il testo valorizzato nel __init__
                return None
        return self.cleaned_data['obiettivo']

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if len(nome) > 200:
            raise forms.ValidationError("La lunghezza del nome di questa lezione non può superare 200 caratteri.")
        return nome

    class Meta:
        model = LezioneCorsoBase
        fields = ['nome', 'docente', 'docente_esterno', 'has_nulla_osta',
                  'inizio', 'fine', 'obiettivo', 'luogo',]
        labels = {
            'nome': 'Lezione',
            'obiettivo': 'Argomento',
        }

    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        self.prefix = kwargs.pop('prefix')

        super().__init__(*args, **kwargs)

        self.order_fields(('nome', 'docente', 'show_docente_esterno', 'docente_esterno',
                           'has_nulla_osta', 'inizio', 'fine', 'obiettivo', 'luogo'))

        # Comportamento campo <docente_esterno>
        show_docente_esterno = self.fields['show_docente_esterno']
        show_docente_esterno.widget.attrs['class'] = 'show_docente_esterno'
        show_docente_esterno.widget.attrs['data-id'] = self.prefix

        if self.has_instance:
            if self.instance.docente_esterno:
                show_docente_esterno.widget.attrs['checked'] = True
            else:
                self.fields['docente_esterno'].widget.attrs['class'] = "docente_esterno_hidden"

        if self.has_instance:
            if self.instance.precaricata:
                lezione = self.instance
                self.initial['obiettivo'] = lezione.get_from_scheda('argomento')

                readonly_fields = ['nome', 'obiettivo']
                for field in readonly_fields:
                    self.fields[field].widget.attrs['readonly'] = True


class ModuloModificaCorsoBase(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['data_inizio', 'data_esame', 'data_esame_2', 'data_esame_pratica',
                  'min_participants', 'max_participants',
                  'descrizione',]
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

        if 'data_esame_pratica' in cd and cd['data_esame_pratica']:
            delta = (cd['data_esame_pratica'] - cd['data_esame']).days
            if delta < 0:
                self.add_error('data_esame_pratica', "Questa data non può essere precedente alla prima data esame")
            if delta > 30:
                self.add_error(
                    'data_esame_pratica',
                    "La prova pratica deve essere svolta nei 30gg successivi alla prima data esame"
                )
        return cd

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        is_nuovo = instance.tipo == Corso.CORSO_NUOVO
        if not is_nuovo:
            self.fields.pop('min_participants')
            self.fields.pop('max_participants')
        else:
            self.fields.pop('data_esame_pratica')

        # The fields are commented because the field's logic was moved to ModuloCreazioneCorsoBase forms step
            # self.fields.pop('titolo_cri')
        # if is_nuovo and instance.stato == Corso.ATTIVO:
        #     self.fields['titolo_cri'].widget.attrs['disabled'] = 'disabled'


class FormModificaCorsoSede(ModelForm):
    locazione = forms.ChoiceField(choices=ModuloCreazioneCorsoBase.LOCAZIONE,
                                  initial=ModuloCreazioneCorsoBase.PRESSO_SEDE,
                                  label='Sede del Corso',)
    class Meta:
        model = CorsoBase
        fields = ['locazione',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        corso = self.instance
        if corso.locazione != corso.sede.locazione:
            self.initial['locazione'] = ModuloCreazioneCorsoBase.ALTROVE


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


class EventoLinkForm(ModelForm):
    class Meta:
        model = EventoFile
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

class ModuloIscrittiCorsoBaseAggiungi(forms.Form):
    persone = autocomplete_light.ModelMultipleChoiceField(
        "IscrivibiliCorsiAutocompletamento",
        help_text="Ricerca per Codice Fiscale discenti da iscrivere a questo Corso.")

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
    titolo = autocomplete_light.ModelMultipleChoiceField("EstensioneLivelloRegionaleTitolo",
        required=False,
        label='Requisiti necessari',
        help_text="Si prega di non compilare questa voce in quanto, qualora il/la Volontario/a non avesse caricato tutte le sue qualifiche su GAIA, "
                  "verrebbe automaticamente escluso dalla possibilità di partecipare al corso, in quanto non riceverebbe alcuna notifica di attivazione del corso")
    sede = autocomplete_light.ModelMultipleChoiceField(
        "EstensioneLivelloRegionaleSede", required=False, label='Selezionare Sede/Sedi')
    # segmento_volontario = forms.ChoiceField(label='Tipo del Volontario')

    class Meta:
        model = CorsoEstensione

        # dall'ordine di questi campi divente il funzionamento di JavaScript
        # in questo template: aspirante_corso_estensioni_modifica.html
        # fields = ['segmento', 'segmento_volontario', 'titolo', 'sede', 'sedi_sottostanti',]
        fields = ['segmento', 'titolo', 'sede', 'sedi_sottostanti',]  # segmento_volontario disattivato

        labels = {
            'segmento': "Destinatari del Corso",
        }
        # widgets = {
        #     'segmento': forms.CheckboxSelectMultiple(
        #         attrs={'class': 'required checkbox form-control'},
        #     ),
        # }

    def clean(self):
        cd = self.cleaned_data

        if self.corso:
            if self.corso.titolo_cri in cd['titolo']:
                self.add_error('titolo', "Non è possibile selezionare lo stesso titolo del Corso.")

        return cd

    def __init__(self, *args, **kwargs):
        self.corso = kwargs.pop('corso')
        super().__init__(*args, **kwargs)

        self.fields['segmento'].choices = [
            (Appartenenza.VOLONTARIO, "Volontari"),
            (Appartenenza.DIPENDENTE, "Dipendenti"),
        ]

        # if self.corso.is_nuovo_corso and self.corso.titolo_cri:
        #     self.fields['titolo'].initial = Titolo.objects.filter(id__in=[
        #         self.corso.titolo_cri.pk])


class ModuloConfermaIscrizioneCorso(forms.Form):
    IS_CORSO_NUOVO = True
    MAX_ISCRIZIONI_CONFERMABILI = 30

    def clean(self):
        cd = self.cleaned_data

        corso = self.instance.corso
        max_iscrizioni = ModuloConfermaIscrizioneCorso.MAX_ISCRIZIONI_CONFERMABILI

        if corso.partecipazioni_confermate().count() >= max_iscrizioni:
            raise ValidationError('Come da regolamento non si possono iscrivere più di %s partecipanti. '
                                  'É raggiunto il limite massimo.' % max_iscrizioni)
        return cd

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')

        super().__init__(*args, *kwargs)


class ModuloConfermaIscrizioneCorsoBase(forms.Form):
    conferma_1 = forms.BooleanField(
        label="Ho incontrato questo aspirante, ad esempio alla presentazione del corso, e mi ha chiesto di essere iscritto al Corso.")
    conferma_2 = forms.BooleanField(
        label="Confermo di voler iscrivere questo aspirante al Corso e comprendo che "
              "questa azione non sarà facilmente reversibile. Sarà comunque possibile "
              "non ammettere l'aspirante all'esame, qualora dovesse non presentarsi "
              "al resto delle lezioni (questo sarà verbalizzato).")


class FormRelazioneDelDirettoreCorso(ModelForm):
    class Meta:
        model = RelazioneCorso
        exclude = ['corso', 'creazione', 'ultima_modifica',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        is_stato_terminato = self.instance.corso.stato == CorsoBase.TERMINATO

        for f in self.fields:
            self.fields[f].label = self.fields[f].help_text
            self.fields[f].widget.attrs['placeholder'] = ''
            self.fields[f].help_text = ''

            if is_stato_terminato:
                self.fields[f].widget.attrs['disabled'] = 'disabled'


class FormVerbaleCorso(ModelForm):
    GENERA_VERBALE = 'genera_verbale'
    SALVA_SOLAMENTE = 'salva'

    class Meta:
        SCHEDA_VALUTAZIONE_CORSO_BASE_FIELDS = ['esito_parte_1',
                                                'argomento_parte_1',
                                                'esito_parte_2',
                                                'argomento_parte_2',
                                                'partecipazione_online',
                                                'extra_1', 'extra_2',
                                                'destinazione',]
        SCHEDA_VALUTAZIONE_CORSO_NUOVO_FIELDS = ['esito_parte_1',
                                                 'esito_parte_2',
                                                 'eventuale_tirocinio',
                                                 'valutazione_complessiva',
                                                 'eventuali_note',]

        model = PartecipazioneCorsoBase
        fields = ['ammissione', 'motivo_non_ammissione',]
        fields.extend(SCHEDA_VALUTAZIONE_CORSO_BASE_FIELDS)
        fields.extend(SCHEDA_VALUTAZIONE_CORSO_NUOVO_FIELDS)

    def __init__(self, *args, generazione_verbale=False, **kwargs):
        self.generazione_verbale = generazione_verbale
        super().__init__(*args, **kwargs)

        instance = self.instance
        corso = instance.corso

        if corso.is_nuovo_corso:
            form_fields = self.Meta.SCHEDA_VALUTAZIONE_CORSO_NUOVO_FIELDS
            self.fields.pop('destinazione')

            self.fields['esito_parte_1'].label = "Parte Teorica"
            self.fields['esito_parte_2'].label = "Parte Pratica"

            for f in ['esito_parte_1', 'esito_parte_2']:
                self.fields[f].help_text = ''
        else:
            form_fields = self.Meta.SCHEDA_VALUTAZIONE_CORSO_BASE_FIELDS

            CHOICES_SENZA_NON_PREVISTO = [ch for ch in self.fields['esito_parte_1'].choices
                                          if ch[0] != PartecipazioneCorsoBase.NON_PREVISTO]
            self.fields['esito_parte_1'].choices = CHOICES_SENZA_NON_PREVISTO
            self.fields['esito_parte_2'].choices = CHOICES_SENZA_NON_PREVISTO
            self.fields['partecipazione_online'].help_text = "<strong>N.B</strong> Da selezionare quando la prova pratica dell'esame è sostituita da colloquio online e la certificazione EFAC non può essere rilasciata"

        # Escludi quei campi che non stanno nella lista di sopra
        for field in self.fields.copy():
            fields_list = ['ammissione', 'motivo_non_ammissione'] + form_fields
            if field not in fields_list:
                self.fields.pop(field)

        # Partecipante non amesso se era assente su questa lezione
        if instance.assente_lezione_salute_e_sicurezza:
            self.fields['ammissione'].choices = [(PartecipazioneCorsoBase.NON_AMMESSO, "Non Ammesso"),]
            self.fields['ammissione'].help_text = "Come da regolamento la lezione Salute e Sicurezza è obbligatoria, " \
                                                  "pertanto non può essere all'esame essendo stato assente."

        if not corso.corso_vecchio:
            if corso.titolo_cri and corso.titolo_cri.scheda_prevede_esame:
                choices = self.fields['ammissione'].choices
                self.fields['ammissione'].choices = [ch for ch in choices if ch[0] != PartecipazioneCorsoBase.ESAME_NON_PREVISTO]
            else:
                # Per i corsi senza esami nascondi i campi non necessari e mostra solo una voce nel campo Ammissione

                # Mostra solo una voca
                self.fields['ammissione'].choices = [
                    (PartecipazioneCorsoBase.ESAME_NON_PREVISTO, "Esame non previsto"),
                    (PartecipazioneCorsoBase.ESAME_NON_PREVISTO_ASSENTE, "Esame non previsto (partecipante assente)"),
                ]

                # Nascondi campi che non servono quando il corso non prevede esame
                for field in self.fields.copy():
                    if field not in ['ammissione',]:
                        self.fields[field] = forms.CharField(required=False, widget=forms.HiddenInput())
                    if field == 'destinazione':
                        self.fields.pop('destinazione')

    def clean_scheda_valutazione_corso_base(self):
        cd = self.cleaned_data

        ammissione = cd['ammissione']
        esito_parte_1, esito_parte_2 = cd.get('esito_parte_1'), cd.get('esito_parte_2')
        argomento_parte_1, argomento_parte_2 = cd.get('argomento_parte_1'), cd.get('argomento_parte_2')
        extra_1, extra_2 = cd.get('extra_1'), cd.get('extra_2')

        # Se non è stato ammesso, un bel gruppo di campi NON devono essere compilati.
        if ammissione != PartecipazioneCorsoBase.AMMESSO:
            non_da_compilare = ['esito_parte_1', 'argomento_parte_1',
                                'esito_parte_2', 'extra_1', 'extra_2',]
            for campo in non_da_compilare:
                if self.cleaned_data.get(campo):
                    self.add_error(campo, "Questo campo deve essere compilato solo nel caso di AMMISSIONE.")

        # Controllo sulla parte 2 del corso
        if esito_parte_2 and extra_2:
            self.add_error('extra_2',
                           "Hai specificato l'esito per la parte 2. Rimuovi l'esito "
                           "della parte due, oppure rimuovi questa opzione.")

        if esito_parte_2 and not argomento_parte_2:
            self.add_error('argomento_parte_2', "Devi specificare l'argomento della seconda parte.")

        if ammissione == PartecipazioneCorsoBase.AMMESSO:
            if not esito_parte_1:
                self.add_error('esito_parte_1', "Devi specificare l'esito di questa parte.")

            if not argomento_parte_1:
                self.add_error('argomento_parte_1', "Devi specificare l'argomento della prima parte.")

            if (not esito_parte_2) and (not extra_2):
                self.add_error('esito_parte_2',
                               "Devi specificare l'esito di questa parte oppure "
                               "selezionare l'opzione per specificare che l'esame "
                               "non includeva questa parte.")

    def clean_scheda_valutazione_corso_nuovo(self):
        cd = self.cleaned_data
        ammissione = cd['ammissione']

        if ammissione == PartecipazioneCorsoBase.AMMESSO:
            for i in ['esito_parte_1', 'esito_parte_2', 'eventuale_tirocinio']:
                if not cd[i]:
                    self.add_error(i, "Devi specificare l'esito di questa parte.")

        if ammissione != PartecipazioneCorsoBase.AMMESSO:
            for i in self.Meta.SCHEDA_VALUTAZIONE_CORSO_NUOVO_FIELDS:
                if cd[i]:
                    self.add_error(i, "Questo campo deve essere compilato solo nel caso di AMMISSIONE.")

    def clean(self):
        """
        Qui va tutta la logica di validazione del modulo di generazione
         del verbale del corso base.
        """

        cd = super().clean()
        ammissione = cd['ammissione']
        motivo_non_ammissione = cd['motivo_non_ammissione']
        destinazione = cd.get('destinazione')

        # Alcuni campi se esame non previsto non vengono mostrati, non validare

        corso = self.instance.corso

        esame_previsto = True == (corso.titolo_cri and corso.titolo_cri.scheda_prevede_esame)
        if esame_previsto:
            # Controlla che non ci siano conflitti (incoerenze) nei dati.
            if ammissione not in [PartecipazioneCorsoBase.NON_AMMESSO,
                                  PartecipazioneCorsoBase.ASSENTE_MOTIVO,]:
                if motivo_non_ammissione:
                    self.add_error('motivo_non_ammissione',
                                   "Questo campo deve essere compilato solo nel caso di "
                                   "Non Ammesso o Assente per motivo giustificato")

            if self.instance.corso.is_nuovo_corso:
                self.clean_scheda_valutazione_corso_nuovo()
            else:
                self.clean_scheda_valutazione_corso_base()

                if not destinazione:
                    self.add_error('destinazione',
                           "È necessario selezionare la Sede presso la quale il Volontario "
                           "diventerà Volontario (nel solo caso di superamento dell'esame).")

            if not motivo_non_ammissione and ammissione in [PartecipazioneCorsoBase.NON_AMMESSO,]:
                self.add_error('motivo_non_ammissione', "Devi specificare la motivazione di non ammissione all'esame.")


class FormCreateDirettoreDelega(ModelForm):
    persona = autocomplete_light.ModelChoiceField('CreateDirettoreDelegaAutocompletamento')
    has_nulla_osta = forms.BooleanField(label='Responsabilità di aver ricevuto nulla osta dal presidente del comitato di appartenenza',
                                        initial=True)

    def clean(self):
        cd = self.cleaned_data
        corso = self.oggetto

        if corso.titolo_cri and corso.titolo_cri.cdf_livello != Titolo.CDF_LIVELLO_IV:
            if corso.direttori_corso().count() >= 1:
                self.add_error('persona', 'I corsi di questo livello possono avere uno ed un solo direttore')

        return cd

    class Meta:
        model = Delega
        fields = ['persona', 'has_nulla_osta',]

    def __init__(self, *args, **kwargs):
        # These attrs are passed in anagrafica.viste.strumenti_delegati()
        for attr in ['me', 'oggetto']:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))
        super().__init__(*args, **kwargs)


class FormCreateResponsabileEventoDelega(ModelForm):
    persona = autocomplete_light.ModelChoiceField('CreateDirettoreDelegaAutocompletamento')

    class Meta:
        model = Delega
        fields = ['persona',]

    def __init__(self, *args, **kwargs):
        # These attrs are passed in anagrafica.viste.strumenti_delegati()
        for attr in ['me', 'oggetto']:
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
            (self.ALL, "A tutti"),
            (self.UNCONFIRMED_REQUESTS, "Preiscritti"),
            (self.CONFIRMED_REQUESTS, "Partecipanti confermati"),
        ]

        if self.instance.concluso:
            CHOICES.append((self.INVIA_QUESTIONARIO,
                            "Invia questionario di gradimento ai partecipanti"))

        super().__init__(*args, **kwargs)
        self.fields['recipient_type'] = forms.ChoiceField(choices=CHOICES, label='Destinatari')


class FormCommissioneEsame(ModelForm):
    class Meta:
        model = CorsoBase
        fields = ['commissione_esame_file', ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')

        esame_nominativi = instance.commissione_esame_names if instance.commissione_esame_names else ''
        esame_nominativi = esame_nominativi.split(', ')

        super().__init__(*args, **kwargs)

        for i in range(5):
            self.fields['nominativo_%s' % i] = forms.CharField(required=False, label='Nominativo')
            try:
                self.fields['nominativo_%s' % i].initial = esame_nominativi[i]
            except IndexError:
                pass


class CatalogoCorsiSearchForm(forms.Form):
    q = forms.CharField(label='')


class ModuloCreaOperatoreSala(forms.Form):
    NOMINA_LOCALI = (
        (RESPONSABILE_AREA, 'Responsabile di sala'),
    )

    NOMINA = (
        (DELEGATO_AREA, 'Operatore di sala'),
        (RESPONSABILE_AREA, 'Responsabile di sala'),
    )

    persona = autocomplete_light.ModelChoiceField('PersonaAutocompletamento')
    nomina = forms.ChoiceField(choices=NOMINA, required=True)
    sede = forms.ChoiceField(choices=())

    def clean(self):
        cd = self.cleaned_data
        if Sede.objects.get(pk=cd['sede']).estensione == LOCALE and cd['nomina'] == DELEGATO_AREA:
            self._errors['nomina'] = self.error_class(['Non puoi aggiungere questa nomina su un comitato Locale'])

        return cd

    @staticmethod
    def popola_scelta(sedi):
        choices = [
            (None, "--------------------------"),
        ]
        for sede in sedi:
            choices.append((sede.pk, sede))

        return choices

    def __init__(self, *args, **kwargs):
        self.locale = kwargs.pop('locale', None)

        super().__init__(*args, **kwargs)

        if self.locale:
            self.fields['nomina'].choices = self.NOMINA_LOCALI

