import xlsxwriter
from io import BytesIO

from django.http import HttpResponse

from anagrafica.costanti import REGIONALE, LOCALE, PROVINCIALE
from .monitoraggio import TypeFormResponsesFabbisogniFormativiTerritorialeCheck, \
    TypeFormResponsesFabbisogniFormativiRagionaleCheck


def donload_comitati_discendenti(sede):
    """
    Scarica il comitato regionale e tutti i comitati locali ad esso collegati
    """
    comitati = sede.ottieni_discendenti(includimi=True).filter(
        estensione__in=[LOCALE, REGIONALE, PROVINCIALE]).order_by(
        '-estensione')
    comitati_completi_list = []
    typeform_completi_list = []

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    bold = workbook.add_format({'bold': True})

    for comitato in comitati:
        if comitato.estensione == 'R':
            delegato = comitato.monitora_fabb_info_regionali()
            typeform = TypeFormResponsesFabbisogniFormativiRagionaleCheck(
                persona=delegato, comitato_id=comitato.id, users_pk=delegato
            )
            typeform.get_responses_for_all_forms()
            a = typeform.all_forms_are_completed
            if a is 1:
                comitati_completi_list.append(comitato)
                typeform_completi_list.append(typeform)
        else:
            delegato = comitato.monitora_fabb_info_regionali()
            typeform = TypeFormResponsesFabbisogniFormativiTerritorialeCheck(
                persona=delegato, comitato_id=comitato.id, users_pk=delegato
            )
            typeform.get_responses_for_all_forms()
            a = typeform.all_forms_are_completed
            if a is 1:
                comitati_completi_list.append(comitato)
                typeform_completi_list.append(typeform)

    for _comitato, _typeform in zip(comitati_completi_list, typeform_completi_list):
        worksheet = workbook.add_worksheet(_comitato.nome[:31])
        # Naming the headers and making them bold
        worksheet.write('A1', 'Question', bold)
        worksheet.write('B1', 'Answer', bold)
        # Adjust the column width.
        worksheet.set_column('A:A', 60)
        worksheet.set_column('B:B', 60)

        # Start from the first cell below the headers.
        row = 1
        col = 0
        if _typeform._set_typeform_context():
            for results in _typeform._retrieve_data().items():
                for result in results[1]:
                    if result['question_parent']:
                        worksheet.write(row, col, result['question_parent']['title'])
                    worksheet.write(row, col, result['question_title'])
                    worksheet.write(row, col + 1, result['answer'])
                    row += 1

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    filename = 'Excel_data.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
