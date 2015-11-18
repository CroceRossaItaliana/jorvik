from django.contrib import admin
from posta.models import Messaggio, Allegato
from posta.models import Destinatario

__author__ = 'alfioemanuele'


@admin.register(Messaggio)
class AdminMessaggio(admin.ModelAdmin):
    search_fields = ['oggetto', 'mittente__codice_fiscale', 'mittente__email', 'mittente__utenza__email']
    list_display = ('oggetto', 'mittente', 'creazione', 'ultimo_tentativo', 'terminato', )
    list_filter = ('creazione', 'terminato', 'ultimo_tentativo',)


@admin.register(Destinatario)
class AdminDestinatario(admin.ModelAdmin):
    search_fields = ['messaggio__creazione', 'messaggio__oggetto', 'persona__codice_fiscale', 'persona__email', 'persona__utenza__email']
    list_display = ('messaggio', 'persona', 'inviato', 'tentativo', 'errore')
    list_filter = ('inviato', 'tentativo', )



admin.site.register(Allegato)
