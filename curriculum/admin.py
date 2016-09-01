from django.contrib import admin

from base.admin import InlineAutorizzazione
from curriculum.models import TitoloPersonale
from curriculum.models import Titolo
from gruppi.readonly_admin import ReadonlyAdminMixin


@admin.register(Titolo)
class AdminTitolo(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["nome", ]
    list_display = ("nome", "tipo", "inseribile_in_autonomia",)
    list_filter = ("tipo", "richiede_conferma", "inseribile_in_autonomia",)


@admin.register(TitoloPersonale)
class AdminTitoloPersonale(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["titolo__nome", "persona__nome", "persona__cognome", "persona__codice_fiscale", ]
    list_display = ("titolo", "persona", "data_ottenimento", "creazione", "certificato",)
    list_filter = ("titolo__tipo", "creazione", "data_ottenimento",)
    raw_id_fields = ("persona", "certificato_da", "titolo",)
    inlines = [InlineAutorizzazione]
