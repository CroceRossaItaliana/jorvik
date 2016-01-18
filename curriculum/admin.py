from django.contrib import admin
from curriculum.models import TitoloPersonale
from curriculum.models import Titolo


@admin.register(Titolo)
class AdminTitolo(admin.ModelAdmin):
    search_fields = ["nome", ]
    list_display = ("nome", "tipo", "inseribile_in_autonomia",)
    list_filter = ("tipo", "richiede_conferma", "inseribile_in_autonomia",)


@admin.register(TitoloPersonale)
class AdminTitoloPersonale(admin.ModelAdmin):
    search_fields = ["titolo__nome", "persona__nome", "persona__cognome", "persona__codice_fiscale", ]
    list_display = ("titolo", "persona", "data_ottenimento", "creazione", "certificato",)
    list_filter = ("titolo__tipo", "creazione", "data_ottenimento",)
    raw_id_fields = ("persona", "certificato_da", "titolo",)