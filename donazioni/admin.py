from django.contrib.admin import TabularInline
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models

from anagrafica.admin import RAW_ID_FIELDS_DELEGA
from anagrafica.models import Delega
from django.contrib import admin

from donazioni.models import Campagna, Etichetta, Donazione, Donatore
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


class InlineDonazione(ReadonlyAdminMixin, TabularInline):
    model = Donazione
    extra = 0
    fields = ('metodo_pagamento', 'donatore', 'importo', 'data',)
    raw_id_fields = ('donatore',)
    formfield_overrides = {
        models.ForeignKey: {'required': False},
    }


@admin.register(Campagna)
class AdminCampagna(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['organizzatore__nome', 'organizzatore__genitore__nome', 'inizio', 'fine', ]
    list_display = ['nome', 'organizzatore', 'inizio', 'fine', ]
    list_filter = ['nome', 'inizio', 'fine']
    raw_id_fields = RAW_ID_FIELDS_CAMPAGNA
    inlines = [InlineDelegaResponsabileCampagna, InlineEtichettaCampagna, InlineDonazione]


@admin.register(Etichetta)
class AdminEtichetta(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['comitato__nome', 'comitato__genitore__nome', 'slug', ]
    list_display = ['id', 'comitato', 'slug', ]
    list_filter = ['comitato', ]
    raw_id_fields = RAW_ID_FIELDS_ETICHETTA


@admin.register(Donazione)
class AdminDonazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['campagna__nome', 'metodo_pagamento', 'modalita_singola_ricorrente', 'donatore']
    list_display = ['id', 'campagna', 'importo', 'data', 'donatore', 'metodo_pagamento', 'modalita_singola_ricorrente', ]
    list_filter = ['metodo_pagamento', 'modalita_singola_ricorrente', 'donatore']
    readonly_fields = ('creazione', 'ultima_modifica',)


@admin.register(Donatore)
class AdminDonatore(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'cognome', 'codice_fiscale', 'email']
    list_display = ['id', 'codice_fiscale', 'nome', 'cognome', 'email']
    list_filter = ['nome', 'cognome', 'codice_fiscale', 'email']
    inlines = [InlineDonazione]
