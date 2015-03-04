from django.contrib import admin
from attivita.models import Partecipazione, Turno, Area, Attivita

__author__ = 'alfioemanuele'

admin.site.register(Attivita)
admin.site.register(Area)
admin.site.register(Turno)
admin.site.register(Partecipazione)