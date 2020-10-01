from importlib import import_module
from collections import OrderedDict
from datetime import datetime

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
from .tasks import generate_elenco
from . import elenchi


SOCI_TIPI_ELENCHI = {
    'volontari': (elenchi.ElencoVolontari, "Elenco dei Volontari"),
    'giovani': (elenchi.ElencoVolontariGiovani, "Elenco dei Volontari Giovani"),
    'servizio-civile': (elenchi.ElencoServizioCivile, "Elenco Servizio Civile"),
    'ivcm': (elenchi.ElencoIVCM, "Elenco IV e CM"),
    'cm': (elenchi.ElencoCM, "Elenco Corpo Militare"),
    'dimessi': (elenchi.ElencoDimessi, "Elenco Dimessi"),
    'riserva': (elenchi.ElencoInRiserva, "Elenco Volontari in Riserva"),
    'trasferiti': (elenchi.ElencoTrasferiti, "Elenco Trasferiti"),
    'dipendenti': (elenchi.ElencoDipendenti, "Elenco dei Dipendenti"),
    'ordinari': (elenchi.ElencoOrdinari, "Elenco dei Soci Ordinari"),
    'estesi': (elenchi.ElencoEstesi, "Elenco dei Volontari Estesi/In Estensione"),
    'soci': (elenchi.ElencoSociAlGiorno, "Elenco dei Soci"),
    'sostenitori': (elenchi.ElencoSostenitori, "Elenco dei Sostenitori"),
    'ex-sostenitori': (elenchi.ElencoExSostenitori, "Elenco degli Ex Sostenitori"),
    'senza-turni': (elenchi.ElencoSenzaTurni, "Elenco dei volontari con zero turni"),
    'elettorato': (elenchi.ElencoElettoratoAlGiorno, "Elenco Elettorato", 'us_elenco_inc_elettorato.html'),
    'titoli': (elenchi.ElencoPerTitoli, "Ricerca dei soci per titoli"),
}


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

        # Patch for py3.5: remember dict order
        ordered_columns = OrderedDict(sorted(ordered_columns.items(), key=lambda x: x[1]))

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
            self._validate_form()
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
        else:
            # Prova a ottenere l'elenco dalla sessione.
            session_elenco = self.request.session.get(elenco_id)
            if session_elenco:
                self.elenco = session_elenco  # class instance from ufficio_soci.elenchi
            else:
                # Se l'elenco non è più in sessione, potrebbe essere scaduto.
                raise ValueError('Elenco non presente in sessione.')

        return self.elenco  # class instance from ufficio_soci.elenchi

    @property
    def elenco_report_type(self):
        elenco = self._get_elenco()

        if hasattr(elenco, 'REPORT_TYPE'):
            return elenco.REPORT_TYPE
        else:
            return ReportElenco.GENERICO

    def form_cleaned_data(self):
        if self.from_celery:

            form_params = self.params['elenco_form']
            if 'ElencoPerTitoli' == self.params['elenco_class']:
                form_params['titoli'] = self.params['elenco_titoli']
            return form_params

        return None

    def _validate_form(self):
        elenco_form_id = 'elenco_modulo_%s' % self.elenco_id

        # Se l'elenco richiede un modulo
        if self.elenco.modulo():
            # Prova a recuperare form.cleaned_data dalla sessione direttamente o dai celery_params
            cleaned_data = self.form_cleaned_data() or \
                           self.request.session.get(elenco_form_id)

            if cleaned_data:
                form = self.elenco.modulo()(cleaned_data)
            else:
                # La form non è stata ancora compilata
                # Redirect non funzionera' con Celery task.
                return redirect("/us/elenco/%s/modulo/" % self.elenco_id)

            # Se il modulo non è valido, qualcosa è andato storto
            if not form.is_valid():
                # Prova nuovamente?
                # Redirect non funzionera' con Celery task.
                return redirect('/us/elenco/%s/modulo/' % self.elenco_id)

            # Imposta il modulo
            self.elenco.modulo_riempito = form

            return self.elenco.modulo_riempito

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
        d = {
            'elenco_id': self.elenco_id,
            'multiple_worksheets': self._multiple_worksheets,
            'sedi': list(self.elenco.args[0].values_list('id', flat=True)),
            'elenco_form': self.request.session.get('elenco_modulo_%s' % self.elenco_id),
            'elenco_class': self._get_elenco().__class__.__name__,
        }

        """
        Quando passo celery_params a Celery, 'elenco_form'['titoli'] prende 
        solo l'ultimo titolo, e non tutti, quindi devo salvare i titoli con 
        un altra chiave e poi rimpostarlo nel metodo form_cleaned_data per poi 
        passarli a _validate_form.
        """
        if isinstance(self._get_elenco(), elenchi.ElencoPerTitoli):
            d['elenco_titoli'] = d['elenco_form'].getlist('titoli')

        return d

    def celery(self, params, report_id):
        # Set some required attributes
        self.celery_multiple_worksheets = params['multiple_worksheets']
        self.elenco_id = params['elenco_id']
        self.params = params

        # Call manually methods
        self._get_elenco(sedi=params['sedi'], elenco_class=params['elenco_class'])
        self._validate_form()
        self._set_intestazione_e_colonne()

        # Do generate report and get bytes-object
        excel = self._generate(save_to_memory=True)

        # Update db record, set status (is_ready) True
        report_db = ReportElenco.objects.get(id=report_id)

        filename = 'Elenco %s %s.xlsx' % (report_db.get_report_type_display(),
                                          report_db.creazione)
        _bytes = ContentFile(excel.output.read())

        report_db.file.save(filename, _bytes, save=True)
        report_db.is_ready = True
        report_db.save()

    @property
    def may_be_downloaded_async(self):
        """
        Ci sono le app (attivita, formazione) che utilizzano questa classe
        per generare elenco. Ma solo nel caso di Elenchi "Soci" dobbiamo
        utilizzare modalita' asincrona per generare e scaricare il file.
        """
        elenco_senza_tesserini = [i[0] for i in SOCI_TIPI_ELENCHI.values()]
        elenco_tesserini = [elenchi.ElencoTesseriniRichiesti,
                            elenchi.ElencoTesseriniDaRichiedere,
                            elenchi.ElencoTesseriniSenzaFototessera,
                            elenchi.ElencoTesseriniRifiutati,]
        elenchi_con_tesserini = elenco_senza_tesserini + elenco_tesserini

        if type(self._get_elenco()) in elenchi_con_tesserini:
            return True
        return False

    @property
    def filename(self):
        if hasattr(self.elenco, 'NAME'):
            s = "%s - %s.xlsx" % (self.elenco.NAME, str(datetime.now().date()))
            return '_'.join(s.split(' '))
        return self.EXCEL_FILENAME

    def download(self):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file = self._generate(save_to_memory=True).output.read()

        response = HttpResponse(file, content_type=content_type)
        response['Content-Disposition'] = "attachment; filename=%s" % self.filename
        return response

    def make(self):
        # Verifica appartenenza dell'elenco richiesto.
        if not self.may_be_downloaded_async:
            return self.download()  # scarica direttamente

        # Create new record in DB
        task_uuid = uuid()
        report_db = ReportElenco(report_type=self.elenco_report_type,
                                 task_id=task_uuid,
                                 user=self.request.user.persona)
        report_db.save()

        # Partire celery task e reindirizza user sulla pagina "Report Elenco"
        task = generate_elenco.apply_async(
            (self.celery_params, report_db.id),
            task_id=task_uuid)

        # Can be that the report is generated immediately, wait a bit
        # and refresh db-record to verify
        from time import sleep
        sleep(2.5)
        report_db.refresh_from_db()

        if report_db.is_ready and report_db.file:
            # If the report is ready, download it without redirect user
            return report_db.download()
        else:
            response = redirect(reverse('ufficio_soci:elenchi_richiesti_download'))
            messages.success(self.request, 'Attendi la generazione del report richiesto.')
            return response
