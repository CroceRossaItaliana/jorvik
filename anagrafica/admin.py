from django.contrib import admin
from anagrafica.models import Persona, Comitato, Appartenenza, Delega, Documento

# Aggiugni al pannello di amministrazione
admin.site.register(Persona)
#admin.site.register(Comitato)
admin.site.register(Appartenenza)
admin.site.register(Delega)
admin.site.register(Documento)
