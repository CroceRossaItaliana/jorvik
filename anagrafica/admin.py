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


admin.site.register(Appartenenza)
admin.site.register(Delega)
admin.site.register(Documento)
admin.site.register(Fototessera)
