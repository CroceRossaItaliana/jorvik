from django.contrib import admin

from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import (Titolo, TitleGoal, TitleLevel, TitoloPersonale)


@admin.register(Titolo)
class AdminTitolo(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', ]
    list_display = ('nome', 'livello_name', 'tipo', 'inseribile_in_autonomia',
        'area', 'goal_obbiettivo_stragetico', 'goal_propedeuticita',
        'goal_unit_reference')
    list_filter = ("tipo", "richiede_conferma", "inseribile_in_autonomia",
                   'livello__goal__unit_reference',)

    def livello_name(self, obj):
        return obj.livello.name if hasattr(obj.livello, 'name') else 'not set'

    def goal_obbiettivo_stragetico(self, obj):
        return obj.livello.goal_obbiettivo_stragetico if hasattr(obj.livello,
                                    'goal_obbiettivo_stragetico') else 'not set'

    def goal_propedeuticita(self, obj):
        return obj.livello.goal_propedeuticita if hasattr(obj.livello,
                                    'goal_propedeuticita') else 'not set'

    def goal_unit_reference(self, obj):
        return obj.livello.goal_unit_reference if hasattr(obj.livello,
                                    'goal_unit_reference') else 'not set'


@admin.register(TitleLevel)
class AdminTitleLevel(admin.ModelAdmin):
    list_display = ['name', 'goal_obbiettivo_stragetico',
                    'goal_propedeuticita', 'goal_unit_reference']
    list_filter = ['goal',]


@admin.register(TitleGoal)
class AdminTitleGoal(admin.ModelAdmin):
    list_display = ['__str__', 'obbiettivo_stragetico', 'propedeuticita',
                    'unit_reference']
    list_filter = ['unit_reference',]


@admin.register(TitoloPersonale)
class AdminTitoloPersonale(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["titolo__nome", "persona__nome", "persona__cognome", "persona__codice_fiscale", ]
    list_display = ("titolo", "persona", "data_ottenimento", "creazione", "certificato",)
    list_filter = ("titolo__tipo", "creazione", "data_ottenimento",)
    raw_id_fields = ("persona", "certificato_da", "titolo",)
    inlines = [InlineAutorizzazione]
