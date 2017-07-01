from collections import defaultdict

import pyexcel


def _importa(formato, file_import, intestazione):
    """
    :param formato: 'csv' o 'xls'
    :param file_import: InMemoryUploadedFile
    :param intestazione: int: numero di righe da saltare all'inizio
    :return: (preview dati, Oggetto Sheet di pyexcel)

        preview = {0: 'A, B, C',
           1: 'TEST 1, TEST 2, TEST 3',
           2: 'AMBA, RABA, CICCI, COCCO'} # dict di stringhe con chiave intera (indice colonna)
        dati = [['A', 'B', 'C',...,],...]  # oggetto Sheet iterabile come lista di liste
    """
    content = file_import.read()
    foglio = pyexcel.get_sheet(file_type=formato, file_content=content, start_row=intestazione)

    # serve per una preview dei dati basata su colonna
    dati_colonna = defaultdict(list)
    for riga in foglio.row[:5]:
        for i, valore in enumerate(riga, start=1):
            dati_colonna[i].append(str(valore))
    preview = {idx: ', '.join(v for v in values if v) for idx, values in dati_colonna.items()}

    return preview, foglio


def analizza_file_import(file_importato, intestazione=0, formato='csv'):
    if formato not in ('csv', 'xls'):
        raise ValueError('Formato non valido %s' % formato)
    return _importa(formato, file_importato, intestazione)
