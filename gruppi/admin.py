from django.contrib import admin
from gruppi.models import Appartenenza, Gruppo

__author__ = 'alfioemanuele'

admin.site.register(Gruppo)
admin.site.register(Appartenenza)