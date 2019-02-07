from django.contrib import admin

from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import (Titolo, TitleGoal, TitoloPersonale)


@admin.register(Titolo)
class AdminTitolo(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', ]
    list_display = ('nome', 'tipo', 'goal_obbiettivo_stragetico', 'goal_propedeuticita',
        'goal_unit_reference', 'inseribile_in_autonomia', 'expires_after', 'area',)
    list_filter = ('is_active', 'cdf_livello', 'area', "tipo", "richiede_conferma",
        "inseribile_in_autonomia", 'goal__unit_reference',)

    def goal_obbiettivo_stragetico(self, obj):
        return obj.goal.unit_reference if hasattr(obj.goal,
                                    'unit_reference') else 'not set'

    def goal_propedeuticita(self, obj):
        return obj.goal.propedeuticita if hasattr(obj.goal,
                                    'propedeuticita') else 'not set'

    def goal_unit_reference(self, obj):
        return obj.goal.get_unit_reference_display() if hasattr(obj.goal,
                                    'unit_reference') else 'not set'

    goal_obbiettivo_stragetico.short_description = 'Obiettivo strategico di riferimento'
    goal_propedeuticita.short_description = 'Propedeuticità'
    goal_unit_reference.short_description = 'Unità  riferimento'


@admin.register(TitleGoal)
class AdminTitleGoal(admin.ModelAdmin):
    list_display = ['__str__', 'obbiettivo_stragetico', 'propedeuticita',
                    'unit_reference']
    list_filter = ['unit_reference',]


@admin.register(TitoloPersonale)
class AdminTitoloPersonale(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["titolo__nome", "persona__nome", "persona__cognome",
                     "persona__codice_fiscale",]
    list_display = ("titolo", "persona", 'is_course_title',
                    "data_ottenimento", 'data_scadenza', "certificato", "creazione",)
    list_filter = ("titolo__tipo", "creazione", "data_ottenimento",
                   'is_course_title')
    raw_id_fields = ("persona", "certificato_da", "titolo",)
    inlines = [InlineAutorizzazione]
