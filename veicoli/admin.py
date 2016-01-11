from django.contrib import admin
from veicoli.models import Autoparco, Veicolo, FermoTecnico, Manutenzione, Segnalazione, Collocazione, \
    Rifornimento

__author__ = 'alfioemanuele'

admin.site.register(Autoparco)
admin.site.register(Veicolo)
admin.site.register(FermoTecnico)
admin.site.register(Manutenzione)
#admin.site.register(Immatricolazione)
admin.site.register(Segnalazione)
admin.site.register(Collocazione)
admin.site.register(Rifornimento)

