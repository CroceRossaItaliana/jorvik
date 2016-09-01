from django.contrib import admin

from base.admin import InlineAutorizzazione
from formazione.models import CorsoBase, PartecipazioneCorsoBase, AssenzaCorsoBase, Aspirante, LezioneCorsoBase
from gruppi.readonly_admin import ReadonlyAdminMixin


__author__ = 'alfioemanuele'

RAW_ID_FIELDS_CORSOBASE = ['sede', 'locazione',]
RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE = ['persona', 'corso']
RAW_ID_FIELDS_LEZIONECORSOBASE = ['corso',]
RAW_ID_FIELDS_ASSENZACORSOBASE = ['lezione', 'persona', 'registrata_da',]
RAW_ID_FIELDS_ASPIRANTE = ['persona', 'locazione',]


class InlinePartecipazioneCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = PartecipazioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE
    extra = 0


class InlineLezioneCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = LezioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    extra = 0


class InlineAssenzaCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = AssenzaCorsoBase
    raw_id_fields = RAW_ID_FIELDS_ASSENZACORSOBASE
    extra = 0


def admin_corsi_base_attivi_invia_messaggi(modeladmin, request, queryset):
    corsi = queryset.filter(stato=CorsoBase.ATTIVO)
    for corso in corsi:
        corso._invia_email_agli_aspiranti()
admin_corsi_base_attivi_invia_messaggi.short_description = "(Solo corsi attivi) Reinvia messaggio di attivazione agli " \
                                                           "aspiranti nelle vicinanze"


@admin.register(CorsoBase)
class AdminCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['sede__nome', 'sede__genitore__nome', 'progressivo', 'anno', ]
    list_display = ['progressivo', 'anno', 'stato', 'sede', 'data_inizio', 'data_esame', ]
    list_filter = ['anno', 'creazione', 'stato', 'data_inizio', ]
    raw_id_fields = RAW_ID_FIELDS_CORSOBASE
    inlines = [InlinePartecipazioneCorsoBase, InlineLezioneCorsoBase]
    actions = [admin_corsi_base_attivi_invia_messaggi]


@admin.register(PartecipazioneCorsoBase)
class AdminPartecipazioneCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'corso__progressivo', ]
    list_display = ['persona', 'corso', 'esito', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE
    inlines = [InlineAutorizzazione]


@admin.register(LezioneCorsoBase)
class AdminLezioneCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'corso__progressivo', 'corso__sede__nome', ]
    list_display = ['corso', 'nome', 'inizio', 'fine', ]
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    inlines = [InlineAssenzaCorsoBase,]


@admin.register(AssenzaCorsoBase)
class AdminAssenzaCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'lezione__corso__progressivo',
                     'lezione__corso__sede__nome']
    list_display = ['persona', 'lezione', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_ASSENZACORSOBASE


def ricalcola_raggio(modeladmin, request, queryset):
    for a in queryset:
        a.calcola_raggio()
ricalcola_raggio.short_description = "Ricalcola il raggio per gli aspiranti selezionati"

@admin.register(Aspirante)
class AdminAspirante(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale']
    list_display = ['persona', 'creazione', ]
    raw_id_fields = RAW_ID_FIELDS_ASPIRANTE
    actions = [ricalcola_raggio,]
