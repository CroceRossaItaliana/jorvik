import xlsxwriter
import tempfile
from anagrafica.costanti import REGIONALE, NAZIONALE


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


def intestazione(workbook, ws):

    nome = ''
    print(type(ws))
    if 'Comitato Regionale ' in ws:
        nome = ws.replace('Comitato Regionale ', '')
    elif 'Comitato dell\'Area Metropolitana di ' in ws:
        nome = ws.replace('Comitato dell\'Area Metropolitana di ', '')
    elif 'Comitato della Provincia Autonoma di ' in ws:
        nome = ws.replace('Comitato della Provincia Autonoma di ', '')
    else:
        nome = ws

    worksheet = workbook.add_worksheet(nome)
    bold = workbook.add_format({'bold': True})
    worksheet.write(0, 0, str('Comitato'), bold)
    worksheet.write(0, 1, str('Genitore'), bold)
    worksheet.write(0, 2, str('Nome metrica'), bold)
    worksheet.write(0, 3, str('Valore'), bold)
    return worksheet


def xlsx_num_soci_vol(obj):

    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)
    bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet('Regionali')
    worksheet.write(0, 0, str('Comitato'), bold)
    worksheet.write(0, 1, str('Nome metrica'), bold)
    worksheet.write(0, 2, str('Valore'), bold)

    count = 1

    if 'regionali' in obj:
        count = inserisci_comitati(worksheet, obj['regionali'], count)

    if 'tot' in obj:
        for el in obj['tot']:
            worksheet.write(count, 0, str(el['nome']), bold)
            count += 1
            for k, v in el['statistiche'].items():
                worksheet.write(count, 0, str(k))
                worksheet.write(count, 1, str(v))
                count += 1

    workbook.close()

    return filename


def xlsx_tot(obj, ws=False):

    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)
    bold = workbook.add_format({'bold': True})

    worksheet = None

    count = 0

    if not ws:
        worksheet = workbook.add_worksheet('Statistiche totali')

    if 'tot' in obj:
        for el in obj['tot']:
            if ws:
                worksheet = workbook.add_worksheet(el['nome'])
                worksheet.write(0, 0, str(el['nome']), bold)
                count = 1
            else:
                worksheet.write(count, 0, str(el['nome']), bold)
                count += 1
            for k, v in el['statistiche'].items():
                worksheet.write(count, 0, str(k))
                worksheet.write(count, 1, str(v))
                count += 1

    workbook.close()

    return filename


def scrivi_comitato(worksheet, count, comitato):
    worksheet.write(count, 0, str(comitato['comitato'].nome) + '(' + comitato['comitato'].estensione + ')')
    worksheet.write(count, 1, str(comitato['comitato'].genitore.nome))
    for k, v in comitato['statistiche'].items():
        worksheet.write(count, 2, str(k))
        worksheet.write(count, 3, str(v))
        count += 1
    return count


def inserisci_comitati_ric(worksheet=None, workbook=None, comitati=[], count=0):

    count = count

    for com in comitati:
        if com['comitato'].estensione == NAZIONALE:
            count = inserisci_comitati_ric(
                workbook=workbook,
                comitati=com['figli'],
                count=1
            )
            break

        if com['comitato'].estensione == REGIONALE:
            worksheet = intestazione(workbook, com['comitato'].nome)
            count = scrivi_comitato(worksheet, 1, com)
        else:
            count = scrivi_comitato(worksheet, count, com)

        if com['figli']:
            count = inserisci_comitati_ric(
                worksheet=worksheet,
                workbook=workbook,
                comitati=com['figli'],
                count=count
            )

    return count


def xlsx_generali(obj, ws=False):
    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)

    bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet('Genarali')

    # HEADER
    worksheet.write(0, 0, str('Nome metrica'), bold)
    worksheet.write(0, 1, str('Valore metrica'), bold)
    worksheet.write(0, 2, str('Rapporti'), bold)
    worksheet.write(0, 3, str('Descrizione'), bold)

    # Numero di Persone
    worksheet.write(1, 0, str('Numero di Persone'))
    worksheet.write(1, 1, str(obj['persone_numero']))
    worksheet.write(1, 2, str(''))
    worksheet.write(1, 3, str('Include tutti i Soggetti registrati su Gaia.'))

    # Numero di Soci CRI
    worksheet.write(2, 0, str('Numero di Soci CRI'))
    worksheet.write(2, 1, str(obj['soci_numero']))
    worksheet.write(2, 2, str(obj['soci_percentuale']) + '% ' + 'delle Persone')
    worksheet.write(2, 3, str('Persone con appartenenza attuale come Socio CRI.'))

    # Numero di Soci CRI Giovani
    worksheet.write(3, 0, str('Numero di Soci CRI Giovani'))
    worksheet.write(3, 1, str(obj['soci_giovani_35_numero']))
    worksheet.write(3, 2, str(obj['soci_giovani_35_percentuale']) + ' % ' + 'dei Soci CRI')
    worksheet.write(3, 3, str('Soci CRI con età inferiore ai 36 anni'))

    # Numero di Sedi CRI
    worksheet.write(4, 0, str('Numero di Sedi CRI'))
    worksheet.write(4, 1, str(obj['sedi_numero']))
    worksheet.write(4, 2, str(''))
    worksheet.write(4, 3, str('Include Sede Nazionale, Regionali, Comitati e Unità Territoriali distaccate.'))

    # Numero di Comitati CRI
    worksheet.write(5, 0, str('Numero di Comitati CRI'))
    worksheet.write(5, 1, str(obj['comitati_numero']))
    worksheet.write(5, 2, str(''))
    worksheet.write(5, 3, str('Include Sede Nazionale, Regionali e Comitati.'))

    workbook.close()

    return filename


def xlsx_comitati_collapse(obj, ws=False):
    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)

    comitati = obj['comitati']

    inserisci_comitati_ric(workbook=workbook, comitati=comitati, count=1)

    workbook.close()

    return filename
