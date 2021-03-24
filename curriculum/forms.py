from django import forms
from django.core.exceptions import ValidationError
from autocomplete_light import shortcuts as autocomplete_light

from anagrafica.models import Appartenenza
from .areas import TITOLO_STUDIO_CHOICES, PATENTE_CIVILE_CHOICES, OBBIETTIVI_STRATEGICI
from .models import Titolo, TitoloPersonale


class ModuloNuovoTitoloPersonale(autocomplete_light.ModelForm):
    class Meta:
        model = TitoloPersonale
        fields = ['titolo',]

    def clean_titolo(self):
        titolo = self.cleaned_data['titolo']
        me = self.me
        
        # Prevent adding the same titles multiple times
        confirmed_titles = me.titoli_confermati()
        if titolo in confirmed_titles:
            raise forms.ValidationError(
                "Hai già inserito questo titolo nel tuo curriculum.")
        
        return titolo

    def __init__(self, tipo, tipo_display, *args, **kwargs):
        # Needs access to the object in clean_titolo()
        # (stored in .views.utente_curriculum)
        self.me = kwargs.pop('me', None)
        super().__init__(*args, **kwargs)
        
        self.fields['titolo'].label = tipo_display
        self.fields['titolo'].queryset = Titolo.objects.filter(
            tipo=tipo,
            inseribile_in_autonomia=True
        )

        """ Add <area> field conditionally"""
        if tipo in [Titolo.TITOLO_CRI, Titolo.TITOLO_STUDIO, Titolo.PATENTE_CIVILE]:
            SELECT_AREA_CHOICES = {
                Titolo.TITOLO_CRI:      OBBIETTIVI_STRATEGICI,  # Titoli CRI (TC)
                Titolo.TITOLO_STUDIO:   TITOLO_STUDIO_CHOICES,  # Titoli di studio (TS)
                Titolo.PATENTE_CIVILE:  PATENTE_CIVILE_CHOICES,  # Patenti civili (PP)
            }
            
            self.fields['area'] = forms.ChoiceField(
                choices=[('', '----')] + SELECT_AREA_CHOICES[tipo],
                required=False,
            )
    
            # Rearrange the order of fields, put <area> before <titolo> field
            self.order_fields(('area', 'titolo',))

        # Override autocomplete's input placeholder attr
        placeholder = 'Inizia a digitare ...'
        if tipo == Titolo.PATENTE_CRI:
            placeholder = 'Scrivi "Patente"'
        self.fields['titolo'].widget.attrs['placeholder'] = placeholder
            

class FormAddQualificaCRI(autocomplete_light.ModelForm):
    titolo = autocomplete_light.ModelChoiceField('QualificaCRIRegressoAutocompletamento')

    class Meta:
        model = TitoloPersonale
        fields = ['titolo', 'data_ottenimento', 'tipo_documentazione', 'attestato_file',
                  'luogo_ottenimento', 'direttore_corso', 'note',]
        help_texts = {
            'data_ottenimento': '',
            'luogo_ottenimento': '',
        }

    def clean(self):
        cd = self.cleaned_data

        email = 'regione@cri.it'

        persona = self.me
        app = persona.appartenenze_attuali(membro__in=[Appartenenza.VOLONTARIO,
                                                       Appartenenza.DIPENDENTE])
        if app:
            app_vo = app.filter(membro=Appartenenza.VOLONTARIO)
            app_di = app.filter(membro=Appartenenza.DIPENDENTE)

            if app_vo or app_di:
                if app_vo:
                    app = app_vo.last()
                elif app_di:
                    app = app_di.last()
            else:
                app = None

            if app and hasattr(app.sede, 'sede_regionale'):
                sede_regionale = app.sede.sede_regionale
                print(sede_regionale)
                # email = sede_regionale.email if hasattr(sede_regionale, 'email') else email
                email = TitoloPersonale.MAIL_FORMAZIONE[sede_regionale.pk]

        show_alert = False
        required_fields = ['titolo', 'data_ottenimento', 'tipo_documentazione', 'attestato_file']

        for field in required_fields:
            if not cd.get(field):
                show_alert = True
                self.add_error(field, 'Campo obbligatorio.')

        if show_alert:
            alert = """Caro Volontario/Dipendente,
                se non sei in possesso di tutte le informazioni richieste per inserire le qualifiche CRI acquisite, 
                ti suggeriamo di rivolgerti al tuo Comitato Regionale (%s) che ti supporterà nella ricerca delle informazioni mancanti. 
                Puoi scrivere una mail indicando il tuo nome, cognome, codice fiscale e indicando le qualifiche da validare 
                ed inserendo tutte le informazioni in tuo possesso in merito. 
                Tutto ciò agevolerà lo staff dedicato a supportarti.""" % email
            raise ValidationError(alert)

    def __init__(self, *args, **kwargs):
        self.me = kwargs.pop('me', None)

        super().__init__(*args, **kwargs)

        self.fields['titolo'].widget.attrs['placeholder'] = 'Inizia a digitare ...'


class ModuloDettagliTitoloPersonale(forms.ModelForm):
    class Meta:
        model = TitoloPersonale
        fields = ['data_ottenimento', 'luogo_ottenimento', 'data_scadenza', 'codice',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True


class FormAddAltreQualifica(autocomplete_light.ModelForm):
    titoli_in_partnership = forms.ChoiceField(
        choices=(),
        required=False
    )
    altri_titolo = autocomplete_light.ModelChoiceField('QualificaAltrePartnershipAutocompletamento', required=False)
    argomento = forms.MultipleChoiceField(required=False, choices=())
    no_corso = forms.BooleanField(initial=False, required=False)
    no_argomento = forms.BooleanField(initial=False, required=False)
    nome_corso = forms.CharField(required=False)
    argomento_nome = forms.CharField(required=False)

    DEFAULT_BLANK_LEVEL = ('', '---------'),

    class Meta:
        model = TitoloPersonale
        fields = [
            'settore_di_riferimento',
            'tipo_altro_titolo',
            'titoli_in_partnership',
            'altri_titolo',
            'no_corso',
            'nome_corso',
            'argomento',
            'no_argomento',
            'argomento_nome',
            'data_ottenimento',
            'attestato_file'
        ]

        help_texts = {
            'data_ottenimento': '',
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['altri_titolo'].widget.attrs['placeholder'] = 'Inizia a digitare ...'
        self.fields['argomento_nome'].label = 'Argomento'
        self.fields['tipo_altro_titolo'].label = 'Tipo Qualifica'
        self.fields['titoli_in_partnership'].label = 'Corsi in partnership con CRI'
        self.fields['argomento'].choices = [
            (argomento, argomento) for choice in Titolo.objects.filter(
                tipo=Titolo.ALTRI_TITOLI) for argomento in choice.argomenti.split(',')
        ]
        self.fields['titoli_in_partnership'].choices = list(self.DEFAULT_BLANK_LEVEL) + [
            (choice.pk, choice) for choice in Titolo.objects.filter(tipo=Titolo.ALTRI_TITOLI, is_partnership=True)
        ]
        self.fields['altri_titolo'].label = 'Corsi esterni'
        self.fields['no_corso'].label = 'Non trovo la mia qualifica'
        self.fields['no_argomento'].label = "Non trovo l'argomento"


class FormAddTitoloStudio(autocomplete_light.ModelForm):

    diploma = autocomplete_light.ModelChoiceField('TitoliStudioDiplomaAutocompletamento', required=False)
    no_diploma = forms.BooleanField(required=False)
    nuovo_diploma = forms.CharField(required=False)
    laurea = autocomplete_light.ModelChoiceField('TitoliStudioLaureaAutocompletamento', required=False)
    no_laurea = forms.BooleanField(required=False)
    nuova_laurea = forms.CharField(required=False)

    class Meta:
        model = TitoloPersonale
        fields = [
            'tipo_titolo_di_studio',
            'diploma',
            'no_diploma',
            'nuovo_diploma',
            'laurea',
            'no_laurea',
            'nuova_laurea',
            'data_ottenimento',
            'attestato_file'
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['diploma'].widget.attrs['placeholder'] = 'Inizia a digitare ...'
        self.fields['no_diploma'].label = 'Non trovo il mio titolo di studio'
        self.fields['no_laurea'].label = 'Non trovo il mio titolo di studio'

        self.fields['laurea'].widget.attrs['placeholder'] = 'Inizia a digitare ...'


class FormAddConoscenzeLinguistiche(autocomplete_light.ModelForm):
    lingua = autocomplete_light.ModelChoiceField('ConoscenzaLinguisticaAutocompletamento', required=False)
    no_lingua = forms.BooleanField(required=False)
    nuova_lingua = forms.CharField(required=False)

    class Meta:
        model = TitoloPersonale
        fields = [
            'lingua',
            'no_lingua',
            'nuova_lingua',
            'livello_linguistico_orale',
            'livello_linguistico_lettura',
            'livello_linguistico_scrittura',
            'data_ottenimento',
            'data_scadenza',
            'attestato_file'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['lingua'].widget.attrs['placeholder'] = 'Inizia a digitare ...'
        self.fields['no_lingua'].label = 'Non trovo la lingua'
        self.fields['livello_linguistico_orale'].label = 'Oralità'
        self.fields['livello_linguistico_lettura'].label = 'Lettura'
        self.fields['livello_linguistico_scrittura'].label = 'Scrittura'


class FormAddCompetenzeSkills(autocomplete_light.ModelForm):
    professione = autocomplete_light.ModelChoiceField('EsperienzeProfessionaliAutocompletamento', required=False)
    no_professione = forms.BooleanField(required=False)
    nuova_professione = forms.CharField(required=False)

    specializzazione = autocomplete_light.ModelChoiceField('SpecializzazioniEsperienzeProfessionaliAutocompletamento', required=False)
    no_specializzazione = forms.BooleanField(required=False)
    nuova_specializzazione = forms.CharField(required=False)

    skill = autocomplete_light.ModelMultipleChoiceField('SkillEsperienzeProfessionaliAutocompletamento', required=False)
    no_skill = forms.BooleanField(required=False)
    nuova_skill = forms.CharField(required=False)

    class Meta:
        model = TitoloPersonale
        fields = [
            'settore_di_riferimento',
            'professione',
            'no_professione',
            'nuova_professione',
            'specializzazione',
            'no_specializzazione',
            'nuova_specializzazione',
            'esperienza',
            'data_ottenimento',
            'data_scadenza',
            'codice_albo',
            'skill',
            'no_skill',
            'nuova_skill',
            'attestato_file',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['settore_di_riferimento'].label = 'Area'
        self.fields['data_ottenimento'].label = 'Data inizio'
        self.fields['data_ottenimento'].help_text = ''
        self.fields['data_scadenza'].label = 'Data fine'
        self.fields['data_scadenza'].help_text = ''
        self.fields['professione'].widget.attrs['placeholder'] = 'Inizia a digitare ...'
        self.fields['specializzazione'].widget.attrs['placeholder'] = 'Inizia a digitare ...'
        self.fields['skill'].widget.attrs['placeholder'] = 'Inizia a digitare ...'

        self.fields['no_professione'].label = 'Non trovo la mia professione'
        self.fields['no_specializzazione'].label = 'Non trovo la mia specializzazione'
        self.fields['no_skill'].label = 'Non trovo le mie skill'
        self.fields['nuova_skill'].label = 'Aggiungi nuove skills separate da (,)'
