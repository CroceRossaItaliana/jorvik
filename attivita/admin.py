from django.contrib import admin
from attivita.models import Partecipazione, Turno, Area, Attivita
from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin


__author__ = 'alfioemanuele'

@admin.register(Attivita)
class AdminAttivita(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'sede__nome', 'estensione__nome', 'area__nome']
    list_display = ('nome', 'sede', 'area', 'estensione', 'stato', 'apertura')
    list_filter = ('creazione', 'stato', 'apertura')
    raw_id_fields = ('locazione', 'sede', 'estensione', 'area', )

@admin.register(Area)
class AdminArea(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'sede__nome', 'obiettivo']
    list_display = ('nome', 'sede', 'obiettivo', 'creazione')
    list_filter = ('creazione', 'obiettivo')
    raw_id_fields = ('sede',)


@admin.register(Turno)
class AdminTurno(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'attivita__nome', 'attivita__sede__nome',]
    list_display = ('nome', 'attivita', 'inizio', 'fine', 'creazione', )
    list_filter = ('inizio', 'fine', 'creazione',)
    raw_id_fields = ('attivita',)


@admin.register(Partecipazione)
class AdminPartecipazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona__codice_fiscale', 'persona__cognome', 'persona__nome', 'turno__nome', 'turno__attivita__nome',]
    list_display = ('turno', 'persona', 'creazione', 'esito',)
    list_filter = ('creazione', 'stato', 'confermata',)
    raw_id_fields = ('persona', 'turno', )
    inlines = [InlineAutorizzazione]
