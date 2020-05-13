from collections import OrderedDict
import xlwt

from django.shortcuts import HttpResponse


class AttivitaReport:
    def __init__(self, filename, **kwargs):
        self.filename = filename

    def generate(self):
        COLUMNS = ['Turno', 'Inizio', 'Fine', 'Partecipanti']
        DATE_FORMAT = '%d/%m/%Y %I:%M'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(self.attivita.nome)

        row_num = 0

        ordered_columns = {i: line for line, i in enumerate(COLUMNS)}
        # Patch for py3.5: remember dict order
        ordered_columns = OrderedDict(sorted(ordered_columns.items(), key=lambda x: x[1]))
        columns = list(ordered_columns.keys())

        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num])

        for turno, partecipanti in self.turni_e_partecipanti:
            row_num += 1

            inizio, fine = turno.inizio.strftime(DATE_FORMAT), turno.fine.strftime(DATE_FORMAT)

            ws.write(row_num, ordered_columns['Turno'], turno.nome)
            ws.write(row_num, ordered_columns['Inizio'], inizio)
            ws.write(row_num, ordered_columns['Fine'], fine)

            partecipanti_cell = list()
            for partecipante in partecipanti:
                partecipanti_cell.append("%s - %s" % (
                    partecipante.codice_fiscale,
                    partecipante.nome_completo
                ))

            partecipanti_cell = partecipanti_cell if partecipanti_cell else ["Nessun partecipante registrato.",]

            ws.write(row_num, ordered_columns['Partecipanti'],
                '\n'.join(partecipanti_cell),
                style
            )

            ws.col(ordered_columns['Turno']).width = int((len(turno.nome)*1)*260)
            ws.col(ordered_columns['Inizio']).width = int(len(inizio)*260)
            ws.col(ordered_columns['Fine']).width = int(len(fine)*260)
            ws.col(ordered_columns['Partecipanti']).width = int(45*260)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 300 * len(partecipanti_cell)

        return wb

    def download(self, generated):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.filename
        generated.save(response)
        return response

    def generate_and_download(self, data, **kwargs):
        self.attivita = data.pop('attivita')
        self.turni_e_partecipanti = data.pop('turni_e_partecipanti')

        return self.download(self.generate())
