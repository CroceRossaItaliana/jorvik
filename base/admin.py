from django.contrib import admin
from base.geo import Locazione
from base.models import Autorizzazione, Token

# Aggiugni al pannello di amministrazione
admin.site.register(Autorizzazione)
admin.site.register(Token)

def locazione_aggiorna(modello, request, queryset):
    for locazione in queryset:
        locazione.cerca_e_aggiorna()
locazione_aggiorna.short_description = "Aggiorna indirizzi selezionati"

@admin.register(Locazione)
class AdminLocazione(admin.ModelAdmin):
    search_fields = ["indirizzo", "via", "comune", "regione", "provincia"]
    list_display = ("indirizzo", "provincia", "regione", "stato", "creazione",)
    list_filter = ("regione", "stato", "creazione")
    actions = [locazione_aggiorna]

