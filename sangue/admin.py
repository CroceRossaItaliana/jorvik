import csv
import io

from django.conf.urls import url
from django.contrib import admin, messages
from django.shortcuts import render

from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from sangue.models import Sede, Donazione, Donatore, Merito


@admin.register(Sede)
class AdminSede(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'regione', 'citta']
    list_display = ('regione', 'provincia', 'citta')
    list_filter = ('regione', 'provincia')

    def get_urls(self):
        urls = super(AdminSede, self).get_urls()
        custom_urls = [
            url(r'^sede/importa/$',
                self.admin_site.admin_view(self.import_sedi),
                name='sangue_sede_import_sedi'),
        ]
        return custom_urls + urls

    def _import_sedi(self, request, file):
        sedi_non_caricati = []

        count = {
            'totale': 0,
            'inserite': 0,
            'non_inserite': 0
        }

        fieldnames = (
            'REGIONE', 'PROVINCIA', 'COMUNE', 'PUNTO DI RACCOLTA'
        )

        reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')), delimiter=',', fieldnames=fieldnames)

        next(reader)
        for row in reader:
            count['totale'] += 1

            regione = row['REGIONE'].lower()
            provincia = row['PROVINCIA'].lower()
            citta = row['COMUNE'].lower()
            nome = row['PUNTO DI RACCOLTA'].lower()

            sede = Sede.objects.filter(
                regione=regione,
                provincia=provincia,
                nome__exact=nome,
                citta=citta
            )

            # Se non esieste lo creo
            if not sede.exists():
                sede = Sede(
                    regione=regione,
                    provincia=provincia,
                    nome=nome,
                    citta=citta
                )
                sede.save()
                count['inserite'] += 1
            else:
                count['non_inserite'] += 1
                sede = sede.first()
                sedi_non_caricati.append(
                    'Sede {} gia esistente'.format(sede)
                )

        return sedi_non_caricati, count

    def import_sedi(self, request):

        contesto = {
            'opts': self.model._meta
        }

        if request.POST:
            files = request.FILES.getlist('file')
            for file in files:
                if not file.name.split('.')[1].lower() in 'csv':
                    messages.error(request, "Il file deve avere un fomato .csv separato da ,")

            sedi_non_caricati, counts = self._import_sedi(request, files[0])

            contesto['counts'] = counts

            if sedi_non_caricati:
                for warning in sedi_non_caricati:
                    messages.warning(request, warning)

        return render(request, 'admin/sangue/importa_sede.html', contesto)


@admin.register(Donatore)
class AdminDonatore(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona', 'gruppo_sanguigno', 'fattore_rh']
    list_display = ('persona', 'gruppo_sanguigno', 'fattore_rh')
    list_filter = ('gruppo_sanguigno', 'fattore_rh')
    raw_id_fields = ('persona', 'sede_sit')


@admin.register(Donazione)
class AdminDonazione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['persona', 'tipo', 'data']
    list_display = ('persona', 'tipo', 'data', 'esito')
    list_filter = ('tipo',)
    raw_id_fields = ('persona', 'sede')
    inlines = [InlineAutorizzazione]
