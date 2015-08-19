from django.contrib import admin
from base.geo import Locazione
from base.models import Autorizzazione, Token

# Aggiugni al pannello di amministrazione
admin.site.register(Autorizzazione)
admin.site.register(Token)
admin.site.register(Locazione)