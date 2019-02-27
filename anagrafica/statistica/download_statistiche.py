import xlsxwriter
import tempfile


def inserisci_comitati(worksheet, comitati, count):

    count = count

    for reg in comitati:
        worksheet.write(count, 0, str(reg['comitato'].nome))
        for k, v in reg['statistiche'].items():
            worksheet.write(count, 1, str(k))
            worksheet.write(count, 2, str(v))
            count += 1

    return count





def inserisci_tot(worksheet, statistiche, count):

    count = count

    for k, v in statistiche.items():
        worksheet.write(count, 0, str(k))
        worksheet.write(count, 1, str(v))
        count += 1

    return count


def intestazione_intestazione(workbook, ws):
    worksheet = workbook.add_worksheet(ws)
    bold = workbook.add_format({'bold': True})
    worksheet.write(0, 0, str('Comitato'), bold)
    worksheet.write(0, 1, str('Nome metrica'), bold)
    worksheet.write(0, 2, str('Valore'), bold)
    return worksheet


