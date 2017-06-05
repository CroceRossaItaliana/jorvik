from django.contrib.admin import TabularInline
from django.contrib.contenttypes.admin import GenericTabularInline

from anagrafica.admin import RAW_ID_FIELDS_DELEGA
from anagrafica.models import Delega
from django.contrib import admin

from donazioni.models import Campagna, Etichetta
from gruppi.readonly_admin import ReadonlyAdminMixin

RAW_ID_FIELDS_CAMPAGNA = ['organizzatore', ]
RAW_ID_FIELDS_ETICHETTA = ['comitato', ]


class InlineDelegaResponsabileCampagna(ReadonlyAdminMixin, GenericTabularInline):
    model = Delega
    raw_id_fields = RAW_ID_FIELDS_DELEGA
    ct_field = 'oggetto_tipo'
    ct_fk_field = 'oggetto_id'
    extra = 0


class InlineEtichettaCampagna(ReadonlyAdminMixin, TabularInline):
    model = Campagna.etichette.through
    extra = 0


@admin.register(Campagna)
class AdminCampagna(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['organizzatore__nome', 'organizzatore__genitore__nome', 'inizio', 'fine', ]
    list_display = ['nome', 'organizzatore', 'inizio', 'fine', ]
    list_filter = ['nome', 'inizio', 'fine']
    raw_id_fields = RAW_ID_FIELDS_CAMPAGNA
    inlines = [InlineDelegaResponsabileCampagna, InlineEtichettaCampagna]


@admin.register(Etichetta)
class AdminEtichetta(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['comitato__nome', 'comitato__genitore__nome', 'nome', ]
    list_display = ['nome', 'comitato', 'slug', ]
    list_filter = ['nome', 'comitato', ]
    raw_id_fields = RAW_ID_FIELDS_ETICHETTA
