import xlsxwriter
from io import BytesIO

from django.db.models import Q
from django.http import HttpResponse

from anagrafica.costanti import REGIONALE, LOCALE, PROVINCIALE
from .models import TypeFormCompilati
from .monitoraggio import TypeFormResponsesFabbisogniFormativiTerritorialeCheck, \
    TypeFormResponsesFabbisogniFormativiRagionaleCheck


def download_excel(sede, comitato, request_path):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    bold = workbook.add_format({'bold': True})
    # xlsxwriter throws an error if the mane of the sheet is more than 31 chars
    worksheet = workbook.add_worksheet(sede.nome[:31])

    # Naming the headers and making them bold
    worksheet.write('A1', 'Question', bold)
    worksheet.write('B1', 'Answer', bold)
    # Adjust the column width.
    worksheet.set_column('A:A', 60)
    worksheet.set_column('B:B', 60)

    # Start from the first cell below the headers.
    row = 1
    col = 0

    if 'territori' in request_path:
        typeform = TypeFormCompilati.objects.filter(
            Q(tipo__icontains='Territoriali') & Q(comitato__pk=int(comitato))).first()
    else:  # regionali
        typeform = TypeFormCompilati.objects.filter(
            Q(tipo__icontains='Regionali') & Q(comitato__pk=int(comitato))).first()

    for results in typeform.results.items():
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


def download_comitati_discendenti(sede, request_path):
    """
    Scarica (excel file) il comitato regionale e tutti i comitati locali ad esso collegati
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
        # if the url is monitora regionali, excel must contain even comitato regionale
        # else must contain only comitati locali discendenti
        if 'regionale' in request_path:
            if comitato.estensione == 'R':
                typeform_db = TypeFormCompilati.objects.filter(
                    Q(tipo__icontains='Regionali') & Q(comitato__pk=comitato.pk)).first()
                if typeform_db:
                    completato_o_no = 1
                else:
                    completato_o_no = 0
                if completato_o_no is 1:
                    comitati_completi_list.append(comitato)
                    typeform_completi_list.append(typeform_db)
            else:
                typeform_db = TypeFormCompilati.objects.filter(
                    Q(tipo__icontains='Territoriali') & Q(comitato__pk=comitato.pk)).first()
                if typeform_db:
                    completato_o_no = 1
                else:
                    completato_o_no = 0
                if completato_o_no is 1:
                    comitati_completi_list.append(comitato)
                    typeform_completi_list.append(typeform_db)
        else:
            typeform_db = TypeFormCompilati.objects.filter(
                Q(tipo__icontains='Territoriali') & Q(comitato__pk=comitato.pk)).first()
            if typeform_db:
                completato_o_no = 1
            else:
                completato_o_no = 0
            if completato_o_no is 1:
                comitati_completi_list.append(comitato)
                typeform_completi_list.append(typeform_db)

    for _comitato, _typeform in zip(comitati_completi_list, typeform_completi_list):
        # xlsxwriter throws an error if the mane of the sheet is more than 31 chars
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
        for results in _typeform.results.items():
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


"""Questo prende il typeform da typeform.com API"""
# def download_comitati_discendenti(sede, request_path):
#     """
#     Scarica (excel file) il comitato regionale e tutti i comitati locali ad esso collegati
#     """
#     comitati = sede.ottieni_discendenti(includimi=True).filter(
#         estensione__in=[LOCALE, REGIONALE, PROVINCIALE]).order_by(
#         '-estensione')
#     comitati_completi_list = []
#     typeform_completi_list = []
#
#     output = BytesIO()
#     workbook = xlsxwriter.Workbook(output)
#     bold = workbook.add_format({'bold': True})
#
#     for comitato in comitati:
#         # if the url is monitora regionali, excel must contain even comitato regionale
#         # else must contain only comitati locali discendenti
#         if 'regionale' in request_path:
#             if comitato.estensione == 'R':
#                 delegato = comitato.monitora_fabb_info_regionali()
#                 typeform = TypeFormResponsesFabbisogniFormativiRagionaleCheck(
#                     persona=delegato, comitato_id=comitato.id, users_pk=delegato
#                 )
#                 typeform.get_responses_for_all_forms()
#                 completato_o_no = typeform.all_forms_are_completed
#                 # se e completato e 1, se non e completato e 0
#                 if completato_o_no is 1:
#                     comitati_completi_list.append(comitato)
#                     typeform_completi_list.append(typeform)
#             else:
#                 delegato = comitato.monitora_fabb_info_regionali()
#                 typeform = TypeFormResponsesFabbisogniFormativiTerritorialeCheck(
#                     persona=delegato, comitato_id=comitato.id, users_pk=delegato
#                 )
#                 typeform.get_responses_for_all_forms()
#                 completato_o_no = typeform.all_forms_are_completed
#                 if completato_o_no is 1:
#                     comitati_completi_list.append(comitato)
#                     typeform_completi_list.append(typeform)
#         else:
#             delegato = comitato.monitora_fabb_info_regionali()
#             typeform = TypeFormResponsesFabbisogniFormativiTerritorialeCheck(
#                 persona=delegato, comitato_id=comitato.id, users_pk=delegato
#             )
#             typeform.get_responses_for_all_forms()
#             completato_o_no = typeform.all_forms_are_completed
#             if completato_o_no is 1:
#                 comitati_completi_list.append(comitato)
#                 typeform_completi_list.append(typeform)
#
#     for _comitato, _typeform in zip(comitati_completi_list, typeform_completi_list):
#         print(_comitato, _typeform, '------------------------------------------------------------')
#         # xlsxwriter throws an error if the mane of the sheet is more than 31 chars
#         worksheet = workbook.add_worksheet(_comitato.nome[:31])
#         # Naming the headers and making them bold
#         worksheet.write('A1', 'Question', bold)
#         worksheet.write('B1', 'Answer', bold)
#         # Adjust the column width.
#         worksheet.set_column('A:A', 60)
#         worksheet.set_column('B:B', 60)
#
#         # Start from the first cell below the headers.
#         row = 1
#         col = 0
#         if _typeform._set_typeform_context():
#             for results in _typeform._retrieve_data().items():
#                 for result in results[1]:
#                     if result['question_parent']:
#                         worksheet.write(row, col, result['question_parent']['title'])
#                     worksheet.write(row, col, result['question_title'])
#                     worksheet.write(row, col + 1, result['answer'])
#                     row += 1
#
#     # Close the workbook before sending the data.
#     workbook.close()
#
#     # Rewind the buffer.
#     output.seek(0)
#
#     # Set up the Http response.
#     filename = 'Excel_data.xlsx'
#     response = HttpResponse(
#         output,
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = 'attachment; filename=%s' % filename
#     return response
