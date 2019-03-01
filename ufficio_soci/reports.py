import xlwt

from django.db.models import Sum, Q
from django.http import HttpResponse

from anagrafica.permessi.costanti import GESTIONE_SOCI
from .models import Quota, Tesseramento


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
