from django.contrib import admin
from base.modelli import Autorizzazione, Giudizio, Commento

# Aggiugni al pannello di amministrazione
admin.site.register(Autorizzazione)
admin.site.register(Giudizio)
admin.site.register(Commento)