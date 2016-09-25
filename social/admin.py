from django.contrib import admin

from social.models import Commento
from gruppi.readonly_admin import ReadonlyAdminMixin


@admin.register(Commento)
class AdminCommento(ReadonlyAdminMixin, admin.ModelAdmin):
    list_display = ['autore', 'commento', 'creazione', ]
    list_filter = ['creazione', ]
    search_fields = ['autore__nome', 'autore__cognome', 'autore__codice_fiscale']
    raw_id_fields = ['autore',]
