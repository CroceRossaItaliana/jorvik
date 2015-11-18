from django.contrib import admin
from formazione.models import Corso, Partecipazione, Assenza, Aspirante

__author__ = 'alfioemanuele'


admin.site.register(Corso)
admin.site.register(Partecipazione)
admin.site.register(Assenza)
admin.site.register(Aspirante)