from django.contrib import admin
from formazione.models import CorsoBase, PartecipazioneCorsoBase, AssenzaCorsoBase, Aspirante, LezioneCorsoBase

__author__ = 'alfioemanuele'

RAW_ID_FIELDS_CORSOBASE = ['sede', 'locazione',]
RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE = ['persona', 'corso']
RAW_ID_FIELDS_LEZIONECORSOBASE = ['corso',]
RAW_ID_FIELDS_ASSENZACORSOBASE = ['lezione', 'persona', 'registrata_da',]
RAW_ID_FIELDS_ASPIRANTE = ['persona', 'locazione',]


class InlinePartecipazioneCorsoBase(admin.TabularInline):
    model = PartecipazioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE
    extra = 0


class InlineLezioneCorsoBase(admin.TabularInline):
    model = LezioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    extra = 0


class InlineAssenzaCorsoBase(admin.TabularInline):
    model = AssenzaCorsoBase
    raw_id_fields = RAW_ID_FIELDS_ASSENZACORSOBASE
    extra = 0


@admin.register(CorsoBase)
class AdminCorsoBase(admin.ModelAdmin):
    search_fields = ['sede__nome', 'sede__genitore__nome', 'progressivo', 'anno', ]
    list_display = ['progressivo', 'anno', 'sede', 'data_inizio', 'data_esame', ]
    list_filter = ['anno', 'creazione', 'data_inizio', ]
    raw_id_fields = RAW_ID_FIELDS_CORSOBASE
    inlines = [InlinePartecipazioneCorsoBase, InlineLezioneCorsoBase]


@admin.register(PartecipazioneCorsoBase)
class AdminPartecipazioneCorsoBase(admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'corso__progressivo', ]
    list_display = ['persona', 'corso', 'esito', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE


@admin.register(LezioneCorsoBase)
class AdminLezioneCorsoBase(admin.ModelAdmin):
    search_fields = ['nome', 'corso__progressivo', 'corso__sede__nome', ]
    list_display = ['corso', 'nome', 'inizio', 'fine', ]
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    inlines = [InlineAssenzaCorsoBase,]


@admin.register(AssenzaCorsoBase)
class AdminAssenzaCorsoBase(admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'lezione__corso__progressivo',
                     'lezione__corso__sede__nome']
    list_display = ['persona', 'lezione', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_ASSENZACORSOBASE


@admin.register(Aspirante)
class AdminAspirante(admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale']
    list_display = ['persona', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_ASPIRANTE
