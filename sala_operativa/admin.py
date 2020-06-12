from django.contrib import admin

from .models import ReperibilitaSO


@admin.register(ReperibilitaSO)
class ReperibilitaSOAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona', 'creato_da', ]
    list_display = ['persona', 'estensione', 'attivazione', 'inizio', 'fine',
                    'creazione', 'creato_da', ]
    list_filter = ['estensione', ]
