from django.contrib import admin

from .models import ReperibilitaSO, ServizioSO, MezzoSO


@admin.register(ReperibilitaSO)
class ReperibilitaSOAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona', 'creato_da', ]
    list_display = ['persona', 'estensione', 'attivazione', 'inizio', 'fine',
                    'creazione', 'creato_da', ]
    list_filter = ['estensione', ]


@admin.register(ServizioSO)
class ServizioSOAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'sede__nome', 'estensione__nome', 'area__nome', ]
    list_display = ['nome', 'inizio', 'fine', 'sede', 'area', 'estensione',
                    'stato', 'apertura', 'creazione', ]
    list_filter = ['creazione', 'stato', 'apertura', ]
    raw_id_fields = ['locazione', 'sede', 'estensione', 'area', ]


@admin.register(MezzoSO)
class MezzoSOAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'creato_da', ]
    list_display = ['nome', 'tipo', 'mezzo_tipo', 'inizio', 'fine',
                    'creato_da', 'creazione', ]
    list_filter = ['creazione', 'tipo', 'mezzo_tipo', ]
