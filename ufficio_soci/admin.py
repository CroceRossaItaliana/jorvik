from django.contrib import admin
from ufficio_soci.models import Dimissione, Tesserino
from ufficio_soci.models import Trasferimento
from ufficio_soci.models import Estensione

__author__ = 'alfioemanuele'

admin.site.register(Estensione)
admin.site.register(Trasferimento)
admin.site.register(Dimissione)
admin.site.register(Tesserino)