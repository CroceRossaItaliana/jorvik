from django.contrib import admin
from patenti.models import Elemento, Patente
from gruppi.readonly_admin import ReadonlyAdminMixin

__author__ = 'alfioemanuele'


class AdminPatente(ReadonlyAdminMixin, admin.ModelAdmin):
    pass

class AdminElemento(ReadonlyAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(Patente, AdminPatente)
admin.site.register(Elemento, AdminElemento)
