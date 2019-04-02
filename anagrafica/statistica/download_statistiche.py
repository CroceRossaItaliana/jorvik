import xlsxwriter
import tempfile
from anagrafica.costanti import REGIONALE, NAZIONALE, LOCALE, TERRITORIALE
from anagrafica.statistica.stat_costanti import COLORI_COMITATI


def inserisci_comitati(worksheet, comitati, count, bold):

    count = count
    isIntestazione = False
    c = 1
    cr = 1

    for el in comitati:
        worksheet.write(count+cr, 0, str(el['comitato'].nome), bold)
        cr += 2
        for k, v in el['statistiche'].items():
            if not isIntestazione:
                worksheet.write(c, count, str(k), bold)
            worksheet.write(c + 1, count, str(v))
            count += 1
        isIntestazione = True
        c += 2
        count = 1

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
    nome_nomitato = ws['comitato'].nome

    if 'Comitato Regionale ' in nome_nomitato:
        nome = nome_nomitato.replace('Comitato Regionale ', '')
    elif 'Comitato dell\'Area Metropolitana di ' in nome_nomitato:
        nome = nome_nomitato.replace('Comitato dell\'Area Metropolitana di ', '')
    elif 'Comitato della Provincia Autonoma di ' in nome_nomitato:
        nome = nome_nomitato.replace('Comitato della Provincia Autonoma di ', '')
    else:
        nome = nome_nomitato

    worksheet = workbook.add_worksheet(nome)
    bold = workbook.add_format({'bold': True})
    c = 0
    worksheet.write(0, c, str('Comitato'), bold)
    c+=1
    worksheet.write(0, c, str('Genitore'), bold)
    c+=1
    for k, v in ws['statistiche'].items():
        worksheet.write(0, c, str(k), bold)
        c += 1

    # imposto una leggenda
    cell_reg = workbook.add_format({'bg_color': COLORI_COMITATI[REGIONALE]})
    cell_loc = workbook.add_format({'bg_color': COLORI_COMITATI[LOCALE]})
    cell_ter = workbook.add_format({'bg_color': COLORI_COMITATI[TERRITORIALE]})
    c += 1
    worksheet.write(5, c, 'Regionale', cell_reg)
    worksheet.write(6, c, 'Locale', cell_loc)
    worksheet.write(7, c, 'Territoriale', cell_ter)

    return worksheet


def xlsx_num_soci_vol(obj):

    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)
    bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet('Regionali')

    count = 1

    if 'regionali' in obj:
        count = inserisci_comitati(worksheet, obj['regionali'], count, bold)

    count += 5
    if 'tot' in obj:
        for el in obj['tot']:
            worksheet.write(1, count, str(el['nome']), bold)
            count += 1
            for k, v in el['statistiche'].items():
                worksheet.write(0, count, str(k), bold)
                worksheet.write(1, count, str(v))
                count += 1

    workbook.close()

    return filename


def xlsx_tot(obj, ws=False):

    new_file, filename = tempfile.mkstemp()

    workbook = xlsxwriter.Workbook(filename)
    bold = workbook.add_format({'bold': True})

    worksheet = None
    isIntestazione = False
    count = 1

    if not ws:
        worksheet = workbook.add_worksheet('Statistiche totali')

    if 'tot' in obj:
        c = 0
        for el in obj['tot']:
            worksheet.write(c+1, 0, str(el['nome']), bold)
            for k, v in el['statistiche'].items():
                if not isIntestazione:
                    worksheet.write(c, count, str(k), bold)
                worksheet.write(c+1, count, str(v))
                count += 1
            isIntestazione = True
            c += 2
            count = 1



    workbook.close()

    return filename


def scrivi_comitato(workbook, worksheet, count, comitato):

    cell_color = workbook.add_format({'bg_color': COLORI_COMITATI[comitato['comitato'].estensione]})

    c = 0
    worksheet.write(count, c, str(comitato['comitato'].nome) + '(' + comitato['comitato'].estensione + ')', cell_color)
    c += 1
    worksheet.write(count, c, str(comitato['comitato'].genitore.nome), cell_color)
    c += 1
    for k, v in comitato['statistiche'].items():
        worksheet.write(count, c, v, cell_color)
        c += 1
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
            worksheet = intestazione(workbook, com)
            count = scrivi_comitato(workbook, worksheet, 1, com)
        else:
            count = scrivi_comitato(workbook, worksheet, count, com)

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
    worksheet.write(1, 1, obj['persone_numero'])
    worksheet.write(1, 2, str(''))
    worksheet.write(1, 3, str('Include tutti i Soggetti registrati su Gaia.'))

    # Numero di Soci CRI
    worksheet.write(2, 0, str('Numero di Soci CRI'))
    worksheet.write(2, 1, obj['soci_numero'])
    worksheet.write(2, 2, str(obj['soci_percentuale']) + '% ' + 'delle Persone')
    worksheet.write(2, 3, str('Persone con appartenenza attuale come Socio CRI.'))

    # Numero di Soci CRI Giovani
    worksheet.write(3, 0, str('Numero di Soci CRI Giovani'))
    worksheet.write(3, 1, obj['soci_giovani_35_numero'])
    worksheet.write(3, 2, str(obj['soci_giovani_35_percentuale']) + ' % ' + 'dei Soci CRI')
    worksheet.write(3, 3, str('Soci CRI con età inferiore ai 36 anni'))

    # Numero di Sedi CRI
    worksheet.write(4, 0, str('Numero di Sedi CRI'))
    worksheet.write(4, 1, obj['sedi_numero'])
    worksheet.write(4, 2, str(''))
    worksheet.write(4, 3, str('Include Sede Nazionale, Regionali, Comitati e Unità Territoriali distaccate.'))

    # Numero di Comitati CRI
    worksheet.write(5, 0, str('Numero di Comitati CRI'))
    worksheet.write(5, 1, obj['comitati_numero'])
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
