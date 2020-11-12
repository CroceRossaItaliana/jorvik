from django.contrib import admin

from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import ReperibilitaSO, ServizioSO, MezzoSO, TurnoSO, PartecipazioneSO, FunzioneSO, OperazioneSO


@admin.register(ReperibilitaSO)
class ReperibilitaSOAdmin(admin.ModelAdmin):
    raw_id_fields = ['persona', 'creato_da', ]
    list_display = ['persona', 'estensione', 'attivazione', 'inizio', 'fine',
                    'creazione', 'creato_da', ]
    list_filter = ['estensione', ]


@admin.register(ServizioSO)
class ServizioSOAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'sede__nome', 'estensione__nome', ]
    list_display = ['nome', 'inizio', 'fine', 'sede', 'estensione',
                    'stato', 'apertura', 'creazione', ]
    list_filter = ['creazione', 'stato', 'apertura', ]
    raw_id_fields = ['locazione', 'sede', 'estensione', ]


@admin.register(TurnoSO)
class AdminTurno(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'attivita__nome', 'attivita__sede__nome',]
    list_display = ['nome', 'attivita', 'inizio', 'fine', 'creazione', ]
    list_filter = ['inizio', 'fine', 'creazione', ]
    raw_id_fields = ['attivita', ]


@admin.register(PartecipazioneSO)
class AdminPartecipazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['turno__nome', 'turno__attivita__nome', ]
    list_display = ('turno', 'reperibilita', 'creazione', )
    list_filter = ('creazione', 'stato', 'confermata',)
    raw_id_fields = ('reperibilita', 'turno', )


@admin.register(MezzoSO)
class MezzoSOAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'creato_da', ]
    list_display = ['nome', 'tipo', 'mezzo_tipo',
                    'creato_da', 'creazione', ]
    list_filter = ['creazione', 'tipo', 'mezzo_tipo', ]


# @admin.register(OperazioneSO)
# class FunzioneSOAdmin(admin.ModelAdmin):
#     search_fields = ['nome', 'settore', ]
#     list_display = ['nome', 'settore',  ]


@admin.register(FunzioneSO)
class FunzioneSOAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'settore', ]
    list_display = ['nome', 'settore',  ]

