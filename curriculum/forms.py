from django import forms
from autocomplete_light import shortcuts as autocomplete_light

from .areas import TITOLO_STUDIO_CHOICES, PATENTE_CIVILE_CHOICES, OBBIETTIVI_STRATEGICI
from .models import Titolo, TitleGoal, TitoloPersonale


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
            
            
class ModuloDettagliTitoloPersonale(forms.ModelForm):
    class Meta:
        model = TitoloPersonale
        fields = ['data_ottenimento', 'luogo_ottenimento', 'data_scadenza',
                  'codice',]

    def __init__(self, *args, **kwargs):
        super(ModuloDettagliTitoloPersonale, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
