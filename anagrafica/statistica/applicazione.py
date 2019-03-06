from django import forms
from curriculum.areas import OBBIETTIVI_STRATEGICI
from formazione.models import Titolo

from .stat_costanti import (
    GENERALI, NUM_VOL_M_F, NUM_SOCI_VOL, NUM_VOL_FASCIA_ETA, NUM_NUOVI_VOL, NUM_DIMESSI, NUM_SEDI,
    NUM_SEDI_NUOVE, NUMERO_CORSI, IIVV_CM, ORE_SERVIZIO, get_type, get_years, TIPO_CHOICES, FILTRO_ANNO
)

from .qs_statistiche import (
    statistica_generale, statistica_num_vol_m_f, statistica_num_soci_vol, statistica_num_vol_fascia_eta,
    statistica_num_nuovi_vol, statistica_num_dimessi, statistica_num_sedi, statistiche_num_sedi_nuove,
    statistica_num_corsi, statistica_iivv_cm, statistica_ore_servizio
)


from .download_statistiche import (
    xlsx_generali, xlsx_num_soci_vol, xlsx_tot, xlsx_comitati_collapse
)

'''
    FUNZIONI CHE CALCOLANO LE STATISTICHE
'''
STATISTICHE = {
    GENERALI: (statistica_generale, ('statistiche_generali.html', ), xlsx_generali),
    NUM_VOL_M_F: (statistica_num_vol_m_f, ('statistiche_per_comitati_collapse.html', ), xlsx_comitati_collapse),
    NUM_SOCI_VOL: (statistica_num_soci_vol, ('statistiche_per_comitati.html', 'statistiche_totali.html', ), xlsx_num_soci_vol),
    NUM_VOL_FASCIA_ETA: (statistica_num_vol_fascia_eta, ('statistiche_per_comitati_collapse.html', ), xlsx_comitati_collapse),
    NUM_NUOVI_VOL: (statistica_num_nuovi_vol, ('statistiche_totali.html', ), xlsx_tot),
    NUM_DIMESSI: (statistica_num_dimessi, ('statistiche_totali.html', ), xlsx_tot),
    NUM_SEDI: (statistica_num_sedi, ('statistiche_totali.html', ), xlsx_tot),
    NUM_SEDI_NUOVE: (statistiche_num_sedi_nuove, ('statistiche_totali.html', ), xlsx_tot),
    NUMERO_CORSI: (statistica_num_corsi, ('statistiche_totali.html', ), xlsx_tot),
    IIVV_CM: (statistica_iivv_cm, ('statistiche_per_comitati_collapse.html', ), xlsx_comitati_collapse),
    ORE_SERVIZIO: (statistica_ore_servizio, ('statistiche_totali.html', ), xlsx_tot),
}


class ModuloStatisticheBase(forms.Form):
    tipo_statistiche = forms.ChoiceField(widget=forms.Select(), choices=get_type(), required=True)
    nome_corso = forms.CharField(required=False)
    livello_riferimento = forms.ChoiceField(widget=forms.Select(), choices=Titolo.CDF_LIVELLI, required=False)
    area_riferimento = forms.ChoiceField(widget=forms.Select(), choices=OBBIETTIVI_STRATEGICI, required=False)
    tipo_filtro = forms.ChoiceField(choices=TIPO_CHOICES, initial=FILTRO_ANNO, widget=forms.RadioSelect())
    anno_di_riferimento = forms.ChoiceField(widget=forms.Select(), choices=get_years(), required=False)
    dal = forms.DateField(required=False)
    al = forms.DateField(required=False)
