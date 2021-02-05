import csv
import io

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.postgres.fields import JSONField
from django.shortcuts import render

from prettyjson import PrettyJSONWidget

from anagrafica.models import Persona
from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import (Titolo, TitleGoal, TitoloPersonale)


@admin.register(Titolo)
class AdminTitolo(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'sigla',]
    list_display = ('nome', 'tipo', 'is_active', 'sigla', 'cdf_livello', 'area',
        'inseribile_in_autonomia', 'richiede_conferma', 'expires_after', 'scheda_prevede_esame',)
    list_filter = ('is_active', 'cdf_livello', 'area', "tipo", "richiede_conferma",
        "inseribile_in_autonomia", 'richiede_conferma', 'goal__unit_reference', 'scheda_prevede_esame',)
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

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
                    "data_ottenimento", 'data_scadenza', "certificato",
                    "creazione", 'corso_partecipazione__corso')
    list_filter = ("titolo__tipo", "creazione", "data_ottenimento",
                   'is_course_title')
    raw_id_fields = ("persona", "certificato_da", "titolo", 'corso_partecipazione',)
    inlines = [InlineAutorizzazione]

    def get_urls(self):
        urls = super(AdminTitoloPersonale, self).get_urls()
        custom_urls = [
            url(r'^albi/$',
                self.admin_site.admin_view(self.import_albi),
                name='anagrafica_titolopersonale_import_albi'),
        ]

        return custom_urls + urls

    def corso_partecipazione__corso(self, obj):
        return obj.corso_partecipazione.corso \
            if hasattr(obj.corso_partecipazione, 'corso') else ''
    corso_partecipazione__corso.short_description = 'Corso Partecipazione'

    def _import_albi(self, request, file):

        qualifiche_non_caricate = []

        fieldnames = (
            'Nome partecipante',
            'Cognome partecipante',
            'Codice fiscale partecipante',
            'Luogo conseguimento',
            'Data Conseguimento',
            'Nome Direttore',
            'Cognome Direttore',
            'Codice fiscale direttore',
            'Qualifica conseguita',
            'Codice Titolo'
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=',', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            persona = None
            cf_persona = row['Codice fiscale partecipante'].strip()
            nome_persona = row['Nome partecipante'].strip()
            cognome_persona = row['Cognome partecipante'].strip()
            if cf_persona:
                persona = Persona.objects.filter(codice_fiscale=cf_persona).first()
            elif nome_persona and cognome_persona:
                persone = Persona.objects.filter(
                    cognome=cognome_persona, nome=nome_persona
                )
                if persone.count() == 1:
                    persona = persone.first()
                else:
                    print('Ci sono Ambiguità')
                    continue
            else:
                print('Non è possibilte trovare la persona senza conosce Codice Fiscale o Nome e cognome')
                continue

            print(persona)


    def import_albi(self, request):

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1] == 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv")

            self._import_albi(request, files[0])

        contesto = {
            'opts': self.model._meta
        }

        return render(request, 'admin/curriculum/import_albi.html', contesto)
