import csv
import io
from datetime import datetime

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

    def get_urls(self):
        urls = super(AdminTitolo, self).get_urls()
        custom_urls = [
            url(r'^titoli/lingua/$',
                self.admin_site.admin_view(self.import_titoli_lingua),
                name='anagrafica_titolo_import_titoli_lingua'),
            url(r'^titoli/studio/$',
                self.admin_site.admin_view(self.import_titoli_studio),
                name='anagrafica_titolo_import_titoli_studio'),
            url(r'^titoli/professionali/$',
                self.admin_site.admin_view(self.import_titoli_professionali),
                name='anagrafica_titolo_import_titoli_professionali'),
        ]

        return custom_urls + urls

    def _import_titoli_lingua(self, request, file):
        titoli_non_caricati = []

        count = {
            'totale': 0,
            'inserite': 0,
            'non_inserite': 0
        }

        fieldnames = (
            'nome',
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=';', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            count['totale'] += 1

            nome = row['nome']

            if not Titolo.objects.filter(tipo=Titolo.CONOSCENZA_LINGUISTICHE, nome__exact=nome.capitalize()).exists():
                titolo = Titolo(tipo=Titolo.CONOSCENZA_LINGUISTICHE, nome=nome.capitalize())
                titolo.save()
                count['inserite'] += 1
            else:
                count['non_inserite'] += 1
                titoli_non_caricati.append('Non è possibilte aggiungere "{}" già esiste un titolo con questo nome'.format(nome))

        return titoli_non_caricati, count

    def import_titoli_lingua(self, request):

        contesto = {
            'opts': self.model._meta
        }

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1].lower() in 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv separato da ;")

            titoli_non_caricate, counts = self._import_titoli_lingua(request, files[0])

            contesto['counts'] = counts

            if titoli_non_caricate:
                for warning in titoli_non_caricate:
                    messages.warning(request, warning)

        return render(request, 'admin/curriculum/import_titoli_lingua.html', contesto)

    def _import_titoli_studio(self, request, file):
        titoli_non_caricati = []

        count = {
            'totale': 0,
            'inserite': 0,
            'non_inserite': 0
        }

        fieldnames = (
            'nome', 'tipo',
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=';', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            count['totale'] += 1
            nome = row['nome']
            tipo = row['tipo']

            if tipo not in [Titolo.DIPLOMA, Titolo.LAUREA]:
                count['non_inserite'] += 1
                titoli_non_caricati.append(
                    'Non è possibilte aggiungere "{}" il tipo non è {} '.format(nome, Titolo.TIPO_TOTOLO_STUDIO)
                )
            elif not Titolo.objects.filter(
                    tipo=Titolo.TITOLO_STUDIO,
                    nome__exact=nome.capitalize(),
                    tipo_titolo_studio=tipo
            ).exists():
                titolo = Titolo(
                    tipo=Titolo.TITOLO_STUDIO,
                    nome=nome.capitalize(),
                    tipo_titolo_studio=tipo
                )
                titolo.save()
                count['inserite'] += 1
            else:
                count['non_inserite'] += 1
                titoli_non_caricati.append(
                    'Non è possibilte aggiungere "{}" già esiste un titolo con questo nome'.format(nome)
                )

        return titoli_non_caricati, count

    def import_titoli_studio(self, request):

        contesto = {
            'opts': self.model._meta
        }

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1].lower() in 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv separato da ;")

            titoli_non_caricate, counts = self._import_titoli_studio(request, files[0])

            contesto['counts'] = counts

            if titoli_non_caricate:
                for warning in titoli_non_caricate:
                    messages.warning(request, warning)

        return render(request, 'admin/curriculum/import_titoli_studio.html', contesto)

    def _import_titoli_professionali(self, request, file):
        titoli_non_caricati = []

        count = {
            'totale': 0,
            'inserite': 0,
            'non_inserite': 0
        }

        fieldnames = (
            'professione', 'specializazioni', 'skills'
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=';', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            count['totale'] += 1
            professione = row['professione']
            specializazioni = row['specializazioni'].split(',')
            skills = row['skills'].split(',')

            titolo = Titolo.objects.filter(
                tipo=Titolo.ESPERIENZE_PROFESSIONALI,
                nome__exact=professione.capitalize(),
            ).first()

            # Se non esieste lo creo
            if not titolo.exists():
                titolo = Titolo(
                    tipo=Titolo.ESPERIENZE_PROFESSIONALI,
                    nome=professione.capitalize()
                )




            titolo.save()

        return titoli_non_caricati, count

    def import_titoli_professionali(self, request):

        contesto = {
            'opts': self.model._meta
        }

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1].lower() in 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv separato da ;")

            titoli_non_caricate, counts = self._import_titoli_professionali(request, files[0])

            contesto['counts'] = counts

            if titoli_non_caricate:
                for warning in titoli_non_caricate:
                    messages.warning(request, warning)

        return render(request, 'admin/curriculum/import_titoli_professionali.html', contesto)


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
        count = {
            'totale': 0,
            'inserite': 0,
            'non_inserite': 0
        }

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
            'codice'
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=';', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            count['totale'] += 1
            # CERCO PERSONA
            persona = None
            cf_persona = row['Codice fiscale partecipante']
            nome_persona = row['Nome partecipante']
            cognome_persona = row['Cognome partecipante']
            if cf_persona:
                persona = Persona.objects.filter(codice_fiscale=cf_persona.strip()).first()
                if not persona:
                    qualifiche_non_caricate.append(
                        self._aggiungi_errore(
                            row,
                            'Non è possibilte trovare la persona il Codice Fiscale Non esiste'.upper()
                        )
                    )
                    continue
            elif nome_persona and cognome_persona:
                persone = Persona.objects.filter(
                    cognome=cognome_persona.strip(), nome=nome_persona.strip()
                )
                if persone.count() == 1:
                    persona = persone.first()
                else:
                    qualifiche_non_caricate.append(self._aggiungi_errore(row, 'Ci sono Ambiguità sulla persona'.upper()))
                    continue
            else:
                qualifiche_non_caricate.append(
                    self._aggiungi_errore(
                        row,
                        'Non è possibilte trovare la persona senza conosce Codice Fiscale o Nome e cognome'.upper()
                    )
                )
                continue

            # Luogo Conseguimento
            luogo_conseguimento = row['Luogo conseguimento'].strip()

            # Data Consegumento
            data = row['Data Conseguimento'].strip()
            data_conseguimento = None
            if data:
                try:
                    data_conseguimento = datetime.strptime(data, '%d/%m/%Y')
                except:
                    qualifiche_non_caricate.append(
                        self._aggiungi_errore(
                            row,
                            'la data {} non segue il formato %d/%m/%Y'.format(data).upper()
                        )
                    )

            # Direttore
            direttore = None
            cf_direttore = row['Codice fiscale direttore']
            nome_direttore = row['Nome Direttore']
            cognome_direttore = row['Cognome Direttore']
            if cf_direttore:
                direttore = Persona.objects.filter(codice_fiscale=cf_direttore.strip()).first()
                if not direttore:
                    qualifiche_non_caricate.append(
                        self._aggiungi_errore(
                            row,
                            'Non è possibilte trovare il direttore il Codice fiscale non esite'.upper()
                        )
                    )
                    continue
            elif nome_direttore and cognome_direttore:
                direttori = Persona.objects.filter(
                    cognome=cognome_direttore.strip(), nome=nome_direttore.strip()
                )

                if direttori.count() == 1:
                    direttore = direttori.first()
                else:
                    qualifiche_non_caricate.append(self._aggiungi_errore(row, 'Ci sono Ambiguità sul direttore'.upper()))
                    continue
            else:
                qualifiche_non_caricate.append(
                    self._aggiungi_errore(
                        row,
                        'Non è possibilte trovare il direttore senza conosce Codice Fiscale o Nome e cognome'.upper()
                    )
                )
                continue

            titolo = None
            codice_qualifica = row['codice']
            nome_qualifica = row['Qualifica conseguita']

            if codice_qualifica:
                titolo = Titolo.objects.filter(sigla=codice_qualifica.strip()).first()
            elif nome_qualifica:
                titoli = Titolo.objects.filter(nome=nome_qualifica.strip())

                if titoli.count() == 1:
                    titolo = titoli.first()
                else:
                    qualifiche_non_caricate.append(
                        self._aggiungi_errore(row, 'Ci sono Ambiguità sul titolo'.upper()))
                    continue
            else:
                qualifiche_non_caricate.append(
                    self._aggiungi_errore(
                        row,
                        'Non è possibilte trovare il titolo senza conosce sigla o Nome Titolo'.upper()
                    )
                )
                continue

            titolo_personale = TitoloPersonale(
                persona=persona,
                titolo=titolo,
                direttore_corso=direttore,
                data_ottenimento=data_conseguimento,
                luogo_ottenimento=luogo_conseguimento,
                is_course_title=True,
                automatica=True
            )
            titolo_personale.save()
            count['inserite'] += 1

        count['non_inserite'] += len(qualifiche_non_caricate)
        return qualifiche_non_caricate, count

    def _aggiungi_errore(self, row, errore):

        return '{} - {} - {} - {} - {} - {} - {} - {} - {} - {} "{}"'.format(
            row['Nome partecipante'] if row['Nome partecipante'] else 'VUOTO',
            row['Cognome partecipante'] if row['Cognome partecipante'] else 'VUOTO',
            row['Codice fiscale partecipante'] if row['Codice fiscale partecipante'] else 'VUOTO',
            row['Luogo conseguimento'] if row['Luogo conseguimento'] else 'VUOTO',
            row['Data Conseguimento'] if row['Data Conseguimento'] else 'VUOTO',
            row['Nome Direttore'] if row['Nome Direttore'] else 'VUOTO',
            row['Cognome Direttore'] if row['Cognome Direttore'] else 'VUOTO',
            row['Codice fiscale direttore'] if row['Codice fiscale direttore'] else 'VUOTO',
            row['Qualifica conseguita'] if row['Qualifica conseguita'] else 'VUOTO',
            row['codice'] if row['codice'] else 'VUOTO',
            errore
        )

    def import_albi(self, request):

        contesto = {
            'opts': self.model._meta
        }

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1].lower() in 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv separato da ;")

            qualifiche_non_caricate, counts = self._import_albi(request, files[0])

            contesto['counts'] = counts

            if qualifiche_non_caricate:
                for warning in qualifiche_non_caricate:
                    messages.warning(request, warning)

        return render(request, 'admin/curriculum/import_albi.html', contesto)
