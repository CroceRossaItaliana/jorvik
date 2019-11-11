from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from anagrafica.admin import RAW_ID_FIELDS_DELEGA
from anagrafica.models import Delega
from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import (CorsoBase, CorsoFile, CorsoEstensione, CorsoLink,
    Aspirante, PartecipazioneCorsoBase, AssenzaCorsoBase, LezioneCorsoBase,
    InvitoCorsoBase, RelazioneCorso)


RAW_ID_FIELDS_CORSOBASE = ['sede', 'locazione', 'titolo_cri',]
RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE = ['persona', 'corso', 'destinazione',]
RAW_ID_FIELDS_INVITOCORSOBASE = ['persona', 'corso', 'invitante',]
RAW_ID_FIELDS_LEZIONECORSOBASE = ['corso', 'docente', 'lezione_divisa_parent',]
RAW_ID_FIELDS_ASSENZACORSOBASE = ['lezione', 'persona', 'registrata_da',]
RAW_ID_FIELDS_ASPIRANTE = ['persona', 'locazione',]
RAW_ID_FIELDS_ESTENSIONE = ['sede', 'titolo',]


class InlineDelegaCorsoBase(ReadonlyAdminMixin, GenericTabularInline):
    model = Delega
    raw_id_fields = RAW_ID_FIELDS_DELEGA
    ct_field = 'oggetto_tipo'
    ct_fk_field = 'oggetto_id'
    extra = 0


class InlinePartecipazioneCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = PartecipazioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE
    extra = 0


class InlineInvitoCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = InvitoCorsoBase
    raw_id_fields = RAW_ID_FIELDS_INVITOCORSOBASE
    extra = 0


class InlineLezioneCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = LezioneCorsoBase
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    extra = 0


class InlineAssenzaCorsoBase(ReadonlyAdminMixin, admin.TabularInline):
    model = AssenzaCorsoBase
    raw_id_fields = RAW_ID_FIELDS_ASSENZACORSOBASE
    extra = 0


class InlineEstensioneCorso(ReadonlyAdminMixin, admin.TabularInline):
    model = CorsoEstensione
    raw_id_fields = RAW_ID_FIELDS_ESTENSIONE
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
    list_display = ['progressivo', 'tipo', 'stato', 'anno', 'sede',
                    'data_inizio', 'data_esame', 'delibera_file_col',]
    list_filter = ['tipo', 'stato', 'titolo_cri__cdf_livello', 'anno', 'creazione', 'data_inizio',]
    raw_id_fields = RAW_ID_FIELDS_CORSOBASE
    inlines = [InlineDelegaCorsoBase, InlinePartecipazioneCorsoBase,
               InlineInvitoCorsoBase, InlineLezioneCorsoBase, InlineEstensioneCorso]
    actions = [admin_corsi_base_attivi_invia_messaggi]

    def delibera_file_col(self, obj):
        from django.utils.html import format_html

        file = obj.delibera_file
        return format_html("""<a href="/media/%s">Delibera</a>""" % file) if file else ''
    delibera_file_col.short_description = 'Delibera'


@admin.register(InvitoCorsoBase)
class AdminInvitoCorsoBase(admin.ModelAdmin):
    list_display = ['persona', 'corso', 'invitante', 'creazione',]
    list_filter = ['ritirata', 'confermata', 'automatica']
    ordering = ['-creazione', ]


@admin.register(CorsoFile)
class AdminCorsoFile(admin.ModelAdmin):
    list_display = ['__str__', 'file', 'is_enabled', 'corso',]
    list_filter = ['is_enabled',]
    raw_id_fields = ('corso',)


@admin.register(CorsoLink)
class AdminCorsoLink(admin.ModelAdmin):
    list_display = ['link', 'is_enabled', 'corso',]
    list_filter = ['is_enabled', ]
    raw_id_fields = ('corso',)


@admin.register(CorsoEstensione)
class AdminCorsoEstensione(admin.ModelAdmin):
    list_display = ['corso', 'is_active', 'segmento', 'sedi_sottostanti']
    raw_id_fields = RAW_ID_FIELDS_ESTENSIONE


@admin.register(PartecipazioneCorsoBase)
class AdminPartecipazioneCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'corso__progressivo', ]
    list_display = ['persona', 'corso', 'esito', 'creazione', ]
    list_filter = ['confermata',]
    raw_id_fields = RAW_ID_FIELDS_PARTECIPAZIONECORSOBASE
    inlines = [InlineAutorizzazione]
    ordering = ['-creazione',]


@admin.register(LezioneCorsoBase)
class AdminLezioneCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'corso__progressivo', 'corso__sede__nome', ]
    list_display = ['corso', 'nome', 'scheda_lezione_num', 'lezione_divisa_parent', 'inizio',
                    'fine',]
    raw_id_fields = RAW_ID_FIELDS_LEZIONECORSOBASE
    inlines = [InlineAssenzaCorsoBase,]


@admin.register(AssenzaCorsoBase)
class AdminAssenzaCorsoBase(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__nome', 'persona__cognome', 'persona__codice_fiscale', 'lezione__corso__progressivo',
                     'lezione__corso__sede__nome']
    list_display = ['persona', 'lezione', 'creazione', 'esonero', 'registrata_da',]
    list_filter = ['esonero',]
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


@admin.register(RelazioneCorso)
class AdminRelazioneCorso(ReadonlyAdminMixin, admin.ModelAdmin):
    list_display = ['corso', 'is_completed',]
    raw_id_fields = ['corso',]
