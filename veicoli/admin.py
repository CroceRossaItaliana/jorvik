from django.contrib import admin
from veicoli.models import Autoparco, Veicolo, FermoTecnico, Manutenzione

__author__ = 'alfioemanuele'

admin.site.register(Autoparco)
admin.site.register(Veicolo)
admin.site.register(FermoTecnico)
admin.site.register(Manutenzione)