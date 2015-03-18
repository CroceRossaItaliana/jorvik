from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from anagrafica.models import Persona, Comitato, Appartenenza, Delega, Documento, Fototessera

# Aggiugni al pannello di amministrazione
@admin.register(Persona)
class AdminPersona(admin.ModelAdmin):
    search_fields = ['nome', 'cognome', 'codice_fiscale', 'utenza__email', 'email_contatto']
    list_display = ('nome', 'cognome', 'utenza', 'email_contatto', 'codice_fiscale', 'data_nascita', 'stato', 'ultima_modifica', )
    list_filter = ('stato', )


@admin.register(Comitato)
class AdminComitato(MPTTModelAdmin):
    search_fields = ['nome', 'genitore__nome']
    list_display = ('nome', 'genitore', 'tipo', 'estensione', 'creazione', 'ultima_modifica', )
    list_filter = ('tipo', 'estensione')

# admin.site.register(Appartenenza)

@admin.register(Appartenenza)
class AdminAppartenenza(admin.ModelAdmin):
    search_fields = ["tipo", "membro", "persona__nome", "persona__cognome", "persona__codice_fiscale",
                     "persona__utenza__email", "comitato__nome"]
    list_display = ("persona", "comitato", "tipo", "attuale", "inizio", "fine", "creazione")
    list_filter = ("membro", "tipo")


# admin.site.register(Delega)
@admin.register(Delega)
class AdminDelega(admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "person__nome", "persona__codice_fiscale", "tipo", "oggetto"]
    list_display = ("tipo", "oggetto", "persona")
    list_filter = ("tipo", "persona")


# admin.site.register(Documento)
@admin.register(Documento)
class AdminDocumento(admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("tipo", "persona")
    list_filter = ("tipo", "persona")


# admin.site.register(Fototessera)
@admin.register(Fototessera)
class AdminFototessera(admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona",)
    list_filter = ("persona",)
