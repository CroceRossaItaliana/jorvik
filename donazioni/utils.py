from collections import OrderedDict

import xlsxwriter.utility
import pyexcel


def _importa(formato, file_import, intestazione, separatore_csv=','):
    """
    :param formato: 'csv' o 'xls'
    :param file_import: InMemoryUploadedFile
    :param intestazione: int: numero di righe da saltare all'inizio
    :return: tupla: (preview dati, Oggetto Sheet di pyexcel)

        colonne_preview = {'A CampoX': 'A, B, C',
           'B CampoY': 'TEST 1, TEST 2, TEST 3',
           'C CampoZ': 'AMBA, RABA, CICCI, COCCO'} # dict di stringhe con chiave intera (indice colonna)
        dati = [['A', 'B', 'C',...,],...]  # oggetto Sheet iterabile come lista di liste
    """
    kwargs = {'file_content': file_import.read(), 'file_type': formato}
    if formato == 'csv':
        kwargs['delimiter'] = separatore_csv
    foglio = pyexcel.get_sheet(**kwargs)
    colonne_preview = _prepara_preview(foglio, intestazione)
    foglio = pyexcel.get_sheet(start_row=intestazione, **kwargs)
    return colonne_preview, foglio


def _prepara_preview(foglio, intestazione=0):
    # prepara una preview dei dati basata su colonna, con i valori delle prime 5 righe
    # include il nome della colonna presumibilmente a riga 0, se intestazione > 0
    dati_colonna = _OrderedDefaultListDict()
    intestazioni_colonna = {}
    for num_riga, riga in enumerate(foglio.row[:5]):
        for i, valore in enumerate(riga):
            if num_riga == 0 and intestazione > 0:  # fuzzy guess
                intestazioni_colonna[i] = valore
                continue
            if num_riga <= intestazione:
                continue
            nome_colonna = '{} {}'.format(colnum_string(i), intestazioni_colonna.get(i))
            dati_colonna[nome_colonna].append(str(valore))
    colonne_preview = OrderedDict()
    for nome_colonna, values in dati_colonna.items():
        colonne_preview[nome_colonna] = ', '.join(v for v in values if v)
    return colonne_preview


def analizza_file_import(file_importato, intestazione=0, formato='csv', separatore_csv=','):
    if formato not in ('csv', 'xls'):
        raise ValueError('Formato non valido %s' % formato)
    return _importa(formato, file_importato, intestazione, separatore_csv=separatore_csv)


def colnum_string(n):
    """
    Mappa l'indice di colonna con il tipico formato Excel per il nome della colonna
    :param n: int: numero colonna del foglio
    :return: stringa corrispondente nel formato lettere

    Esempio:
    >>> print(colnum_string(28))
    <<< 'AB'
    """
    return xlsxwriter.utility.xl_col_to_name(n)


class _OrderedDefaultListDict(OrderedDict):
    def __missing__(self, key):
        self[key] = value = []
        return value
