from importlib import import_module

from django.db.models import Sum, Q
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages

import xlwt
from celery import uuid

from anagrafica.permessi.costanti import GESTIONE_SOCI
from .models import Quota, Tesseramento, ReportElenco
from .tasks import generate_elenco_soci_al_giorno


class ReportRicevute:
    def __init__(self, me, form=None):
        self.me = me
        self.sedi = me.oggetti_permesso(GESTIONE_SOCI)

        # Initial values
        self.tipi = [x[0] for x in Quota.TIPO]
        self.anno = Tesseramento.ultimo_anno()

        if form is not None and form.is_valid():
            cd = form.cleaned_data
            self.tipi = cd.get('tipi_ricevute')
            self.anno = cd.get('anno')

    @property
    def tipi_testo(self):
        return [dict(Quota.TIPO)[t] for t in self.tipi]

    @property
    def queryset(self):
        return Quota.objects.filter(
            Q(Q(sede__in=self.sedi) | Q(appartenenza__sede__in=self.sedi)),
            anno=self.anno,
            tipo__in=self.tipi,
        ).order_by('progressivo')

    @property
    def importo_totale(self):
        non_annullate = self.queryset.filter(stato=Quota.REGISTRATA)
        importo = non_annullate.aggregate(Sum('importo'))['importo__sum'] or 0.0
        importo_extra = non_annullate.aggregate(Sum('importo_extra'))['importo_extra__sum'] or 0.0
        return importo + importo_extra

    def make_excel(self):
        row_num = 0
        ordered_columns = {i: line for line, i in enumerate(
            ['Num', 'Tipo', 'Pagante', 'CF', 'Importo', 'Data',
             'Registrazione', 'RegistrazioneData', 'Annullamento'])}
        columns = list(ordered_columns.keys())

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Ricevute')

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num])

        col_num = ordered_columns
        for ricevuta in self.queryset:
            row_num += 1

            annullata = ' (ANNULATA)' if ricevuta.stato == ricevuta.ANNULLATA else ''
            num = "%s / %s" % (ricevuta.anno, ricevuta.progressivo)

            ws.write(row_num, col_num['Num'], num + annullata)
            ws.write(row_num, col_num['Tipo'], ricevuta.tipo)
            ws.write(row_num, col_num['Pagante'], str(ricevuta.persona))
            ws.write(row_num, col_num['CF'], ricevuta.persona.codice_fiscale)
            ws.write(row_num, col_num['Importo'], str(ricevuta.importo_totale) + '€')
            ws.write(row_num, col_num['Data'], ricevuta.data_versamento.strftime('%d/%m/%Y'))
            ws.write(row_num, col_num['Registrazione'], str(ricevuta.registrato_da))
            ws.write(row_num, col_num['RegistrazioneData'], ricevuta.creazione.strftime('%d/%m/%Y %I:%M'))

            if ricevuta.data_annullamento:
                ws.write(row_num, col_num['Annullamento'], ricevuta.data_annullamento.strftime('%d/%m/%Y'))

        return wb

    def download(self):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Ricevute.xls'
        self.make_excel().save(response)
        return response


class ReportElencoSoci:
    EXCEL_FILENAME = 'Elenco.xlsx'
    DEFAULT_WORKSHEET = 'Foglio 1'

    def __init__(self, request=None, elenco_id=None, from_celery=False):
        self.from_celery = from_celery
        self.request = request
        self.elenco_id = elenco_id

        if not from_celery:
            self._get_elenco()
            self._check_modulo()
            self._set_intestazione_e_colonne()

    def _set_intestazione_e_colonne(self):
        self.intestazione = [x[0] for x in self.excel_colonne]
        self.colonne = [x[1] for x in self.excel_colonne]

    @property
    def excel_colonne(self):
        return self.elenco.excel_colonne()

    def _simplify_name(self, nome):
        return nome.replace("/", '')\
            .replace(": ", '-').replace("Comitato ", '').replace("Locale ", '')\
            .replace("Provinciale ", '').replace("Di ", '').replace("di ", '')\
            .replace("Della ", '').replace("Dell'", '').replace("Del ", '')

    def _get_elenco(self, **kwargs):
        elenco_id = 'elenco_%s' % self.elenco_id

        if self.from_celery:
            elenchi = import_module('ufficio_soci.elenchi')
            elenco = getattr(elenchi, kwargs['elenco_class'])
            self.elenco = elenco(kwargs.get('sedi'))

            return self.elenco  # class instance from ufficio_soci.elenchi
        else:
            # Prova a ottenere l'elenco dalla sessione.
            session_elenco = self.request.session.get(elenco_id)
            if session_elenco:
                self.elenco = session_elenco  # class instance from ufficio_soci.elenchi
                return session_elenco

            # Se l'elenco non è più in sessione, potrebbe essere scaduto.
            raise ValueError('Elenco non presente in sessione.')

    @property
    def elenco_report_type(self):
        return self._get_elenco().REPORT_TYPE

    def _get_elenco_form(self, celery_elenco_form=None):
        elenco_form_id = 'elenco_modulo_%s' % self.elenco_id

        # Prova a recuperare la form compilata
        session_elenco_form = celery_elenco_form or self.request.session.get(elenco_form_id)
        if session_elenco_form:
            return self.elenco.modulo()(session_elenco_form)

        # La form non è stata ancora compilata
        return redirect("/us/elenco/%s/modulo/" % self.elenco_id)

    def _check_modulo(self, celery_elenco_form=None):
        # Se l'elenco richiede un modulo
        if self.elenco.modulo():
            self.form = self._get_elenco_form(celery_elenco_form)

            # Se il modulo non è valido, qualcosa è andato storto
            if not self.form.is_valid():
                return redirect('/us/elenco/%s/modulo/' % self.elenco_id)  # Prova nuovamente?

            # Imposta il modulo
            self.elenco.modulo_riempito = self.form

    def persone(self):
        from django.core.paginator import Paginator

        qs = self.elenco.ordina(self.elenco.risultati())
        splitted = Paginator(qs, 10000)
        for i in splitted.page_range:
            current_page = splitted.page(i)
            current_qs = current_page.object_list
            yield current_qs

    @property
    def _multiple_worksheets(self):
        if self.request is not None:
            return False if 'foglio_singolo' in self.request.GET else True
        else:
            return self.celery_multiple_worksheets

    def _ws_name(self, person):
        if self._multiple_worksheets:
            return self._simplify_name(self.elenco.excel_foglio(person))[:31]
        return self.DEFAULT_WORKSHEET

    def _generate(self, save_to_memory=False):
        from base.files import Excel, FoglioExcel

        worksheets = dict()
        excel = Excel()

        if not self._multiple_worksheets:
            self.intestazione += ['Elenco']

        for queryset in self.persone():
            for person in queryset:
                ws_name = self._ws_name(person)
                ws_key = ws_name.lower().strip()

                if ws_key not in [x.lower() for x in worksheets.keys()]:
                    worksheets.update({
                        ws_key: FoglioExcel(ws_name, self.intestazione)
                    })

                person_columns = [y if y is not None else '' for y in [x(person) for x in self.colonne]]
                if not self._multiple_worksheets:
                    person_columns += [self.elenco.excel_foglio(person)]

                worksheets[ws_key].aggiungi_riga(*person_columns)

        excel.fogli = worksheets.values()
        excel.genera_e_salva(self.EXCEL_FILENAME, save_to_memory=save_to_memory)
        return excel

    @property
    def celery_params(self):
        return {
            'elenco_id': self.elenco_id,
            'multiple_worksheets': self._multiple_worksheets,
            'sedi': list(self.elenco.args[0].values_list('id', flat=True)),
            'elenco_form': self.request.session.get('elenco_modulo_%s' % self.elenco_id),
            'elenco_class': self._get_elenco().__class__.__name__,
        }

    def celery(self, params, report_id):
        # Set manually some required attributes
        self.celery_multiple_worksheets = params['multiple_worksheets']
        self.elenco_id = params['elenco_id']
        self._get_elenco(sedi=params['sedi'], elenco_class=params['elenco_class'])
        self._check_modulo(celery_elenco_form=params['elenco_form'])

        # Call manually methods
        self._set_intestazione_e_colonne()

        # Do generate report and get bytes-object
        excel = self._generate(save_to_memory=True)

        # Update db record, set status (is_ready) True
        report_db = ReportElenco.objects.get(id=report_id)

        filename = 'Elenco-%s-%s.xlsx' % (report_db.get_report_type_display(),
                                          report_db.creazione)
        _bytes = ContentFile(excel.output.read())

        report_db.file.save(filename, _bytes, save=True)
        report_db.is_ready = True
        report_db.save()

    def make(self):
        # Create new record in DB
        task_uuid = uuid()
        report_db = ReportElenco(report_type=self.elenco_report_type,
                                 task_id=task_uuid,
                                 user=self.request.user.persona)
        report_db.save()

        # Partire celery task e reindirizza user sulla pagina "Report Elenco"
        task = generate_elenco_soci_al_giorno.apply_async(
            (self.celery_params, report_db.id),
            task_id=task_uuid)

        # Can be that the report is generated immediately, wait a bit
        # and refresh db-record to verify
        from time import sleep
        sleep(4)
        report_db.refresh_from_db()

        if report_db.is_ready and report_db.file:
            # If the report is ready, download it without redirect user
            return report_db.download()
        else:
            response = redirect(reverse('elenchi_richiesti_download'))
            messages.success(self.request, 'Attendi la generazione del report richiesto.')
            return response
