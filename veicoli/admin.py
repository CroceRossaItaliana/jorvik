from django.contrib import admin
from veicoli.models import Autoparco, Veicolo, FermoTecnico, Manutenzione, Segnalazione, Collocazione, \
    Rifornimento

__author__ = 'alfioemanuele'

#admin.site.register(Immatricolazione)
#admin.site.register(Segnalazione)


@admin.register(Autoparco)
class AdminAutoparco(admin.ModelAdmin):
    search_fields = ["nome", "sede__nome", ]
    list_display = ("nome", "sede", "telefono", "locazione",)
    list_filter = ("creazione",)
    raw_id_fields = ("sede", )


@admin.register(Veicolo)
class AdminVeicolo(admin.ModelAdmin):
    search_fields = ["targa", "libretto", "telaio", ]
    list_display = ("targa", "libretto", "telaio", "marca", "modello",)
    list_filter = ("stato",)


@admin.register(FermoTecnico)
class AdminFermoTecnico(admin.ModelAdmin):
    search_fields = ["veicolo__targa", ]
    list_display = ("veicolo", "inizio", "fine", "attuale", "motivo",)
    list_filter = ("creazione", "inizio", "fine",)
    raw_id_fields = ("veicolo", "creato_da")


@admin.register(Collocazione)
class AdminCollocazione(admin.ModelAdmin):
    search_fields = ["veicolo__targa", "autoparco__nome", "autoparco__sede__nome", ]
    list_display = ("veicolo", "autoparco", "inizio", "fine", "attuale",)
    list_filter = ("fine", "inizio",)
    raw_id_fields = ("autoparco", "veicolo", "creato_da",)


@admin.register(Rifornimento)
class AdminRifornimento(admin.ModelAdmin):
    search_fields = ["veicolo__targa", ]
    list_display = ("veicolo", "data", "creazione",)
    list_filter = ("data",)
    raw_id_fields = ("veicolo",)


@admin.register(Manutenzione)
class AdminManutenzione(admin.ModelAdmin):
    search_fields = ["veicolo__targa", ]
    list_display = ("veicolo", "tipo", "data", "creato_da",)
    list_filter = ("tipo",)
    raw_id_fields = ("veicolo", "creato_da",)

