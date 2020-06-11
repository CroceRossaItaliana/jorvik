from django.contrib import admin

from .models import ReperibilitaSO


@admin.register(ReperibilitaSO)
class ReperibilitaSOAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona', ]
    list_display = ['persona', 'attivazione', 'inizio', 'fine', ]
