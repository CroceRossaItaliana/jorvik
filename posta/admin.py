from django.contrib import admin
from posta.models import Messaggio, Allegato
from posta.models import Destinatario

__author__ = 'alfioemanuele'

admin.site.register(Messaggio)
admin.site.register(Destinatario)
admin.site.register(Allegato)