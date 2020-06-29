from django.contrib import admin

from .models import ReperibilitaSO, ServizioSO


@admin.register(ReperibilitaSO)
class ReperibilitaSOAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona', 'creato_da', 'servizio', ]
    list_display = ['persona', 'estensione', 'attivazione', 'inizio', 'fine',
                    'creazione', 'creato_da', ]
    list_filter = ['estensione', ]


@admin.register(ServizioSO)
class ServizioSOAdmin(admin.ModelAdmin):
    list_display = ['name', 'inizio', 'fine', 'estensione', 'creato_da',
                    'creazione', ]
    raw_id_fields = ['creato_da', ]
