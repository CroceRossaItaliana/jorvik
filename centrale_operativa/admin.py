from django.contrib import admin, messages

from .models import *

@admin.register(Reperibilita)
class ReperibilitaAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona',]


