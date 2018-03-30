from django.contrib import admin
from posta.models import Messaggio
from posta.models import Destinatario
from gruppi.readonly_admin import ReadonlyAdminMixin

__author__ = 'alfioemanuele'


class AdminDestinatarioInline(ReadonlyAdminMixin, admin.TabularInline):
    model = Destinatario
    search_fields = ['messaggio__oggetto', 'persona__codice_fiscale', 'persona__email_contatto',
                     'persona__utenza__email', 'errore',]
    list_display = ('messaggio', 'persona', 'inviato', 'tentativo', 'errore')
    list_filter = ('inviato', 'tentativo', )
    raw_id_fields = ('persona', 'messaggio',)


@admin.register(Messaggio)
class AdminMessaggio(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['oggetto', 'mittente__codice_fiscale', 'mittente__email_contatto', 'mittente__utenza__email']
    list_display = ('oggetto', 'mittente', 'creazione', 'ultimo_tentativo', 'terminato', )
    list_filter = ('creazione', 'terminato', 'ultimo_tentativo',)
    raw_id_fields = ('mittente', 'rispondi_a')
    inlines = [AdminDestinatarioInline]


@admin.register(Destinatario)
class AdminDestinatario(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['messaggio__oggetto', 'persona__codice_fiscale', 'persona__email_contatto',
                     'persona__utenza__email', 'errore',]
    list_display = ('messaggio', 'persona', 'inviato', 'tentativo', 'errore')
    list_filter = ('inviato', 'tentativo', )
    raw_id_fields = ('persona', 'messaggio',)
