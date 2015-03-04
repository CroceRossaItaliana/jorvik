from django.contrib import admin
from base.models import Autorizzazione, Token

# Aggiugni al pannello di amministrazione
admin.site.register(Autorizzazione)
admin.site.register(Token)