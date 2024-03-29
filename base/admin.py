from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from gruppi.readonly_admin import ReadonlyAdminMixin
from .geo import Locazione
from .models import Autorizzazione, Token, Allegato, Menu, MenuSegmento


@admin.register(Token)
class TokenAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    pass


class MenuSegmentoInline(ReadonlyAdminMixin, admin.TabularInline):
    model = MenuSegmento
    extra = 1
    raw_id_fields = ('sede', 'titolo')

@admin.register(Menu)
class MenuAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
    inlines = (MenuSegmentoInline, )
    list_display = ['url', 'order', 'is_active', 'name', 'menu']

@admin.register(MenuSegmento)
class MenuSegmentoAdmin(ReadonlyAdminMixin, admin.ModelAdmin):
   pass

def locazione_aggiorna(modello, request, queryset):
    for locazione in queryset:
        locazione.cerca_e_aggiorna()
locazione_aggiorna.short_description = "Aggiorna indirizzi selezionati"


class InlineAutorizzazione(ReadonlyAdminMixin, GenericTabularInline):
    model = Autorizzazione
    raw_id_fields = ["richiedente", "firmatario"]
    ct_field = 'oggetto_tipo'
    ct_fk_field = 'oggetto_id'
    extra = 0


@admin.register(Locazione)
class AdminLocazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["=id", "indirizzo", "via", "comune", "regione", "provincia"]
    list_display = ("indirizzo", "provincia", "regione", "stato", "creazione",)
    list_filter = ("regione", "stato", "creazione")
    actions = [locazione_aggiorna]


@admin.register(Autorizzazione)
class AdminAutorizzazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["richiedente__nome", "richiedente__cognome", "richiedente__codice_fiscale",
                     "firmatario__nome", "firmatario__cognome", "firmatario__codice_fiscale", ]
    list_display = ("richiedente", "firmatario", "concessa", 'automatica',
                    "necessaria", "progressivo", "oggetto_tipo", "oggetto_id",
                    "destinatario_ruolo",
                    "destinatario_oggetto_tipo", "destinatario_oggetto_id")
    list_filter = ("necessaria", "concessa", 'automatica', "destinatario_oggetto_tipo",)
    raw_id_fields = ("richiedente", "firmatario", )


@admin.register(Allegato)
class AdminAllegato(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["nome"]
    list_display = ["nome", "creazione", "file"]
    list_filter = ("creazione",)
