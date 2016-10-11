from django.contrib import admin
from gruppi.models import Appartenenza, Gruppo
from gruppi.readonly_admin import ReadonlyAdminMixin

__author__ = 'alfioemanuele'


class AdminGruppo(ReadonlyAdminMixin, admin.ModelAdmin):
    pass

class AdminAppartenenza(ReadonlyAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(Gruppo, AdminGruppo)
admin.site.register(Appartenenza, AdminAppartenenza)
