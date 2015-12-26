from django.contrib import admin
from ufficio_soci.models import Dimissione, Tesserino, Quota, Tesseramento

__author__ = 'alfioemanuele'

admin.site.register(Dimissione)
admin.site.register(Tesserino)
admin.site.register(Quota)
admin.site.register(Tesseramento)