import os
from datetime import datetime, date
from zipfile import ZipFile

from barcode import generate
from barcode.writer import ImageWriter
from django.core.files import File
from django.template import Context
from django.template.loader import get_template

from base.models import Allegato
from base.stringhe import domani, GeneratoreNomeFile
from jorvik.settings import MEDIA_ROOT, DOMPDF_ENDPOINT
from io import StringIO
import urllib
import xlsxwriter

__author__ = 'alfioemanuele'


class Zip(Allegato):
    """
    Rappresenta un file ZIP generato al volo.
    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Zip, self).__init__(*args, **kwargs)
        self._file_in_attesa = []

    def aggiungi_file(self, file_path, nome_file=None):
        """
        Aggiunge un file alla coda del file ZIP.
        Per comprimere tutti i file aggiunti, bisogna chiamare il metodo comprimi()
        :param file_path: Un path completo al file.
        :param nome_file: Il nome del file all'interno dell'archivio. Opzionale, default nome del file.
        :return:
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError("ZIP: Impossibile aggiungere " + str(file_path) + " (non trovato)")
        if nome_file is None:
            nome_file = os.path.basename(file_path)
        self._file_in_attesa.append((file_path, nome_file))

    def comprimi(self, nome='Archivio.zip'):
        """
        Salva il file compresso su disco e svuota la coda.
        Necessario salvare su database per persistere le modifiche.
        :param nome:
        :return:
        """
        generatore = GeneratoreNomeFile('allegati/')
        zname = generatore(self, nome)
        self.prepara_cartelle(MEDIA_ROOT + zname)
        with ZipFile(MEDIA_ROOT + zname, 'w') as zf:
            for f_path, f_nome in self._file_in_attesa:
                zf.write(f_path, f_nome)
            zf.close()

        self.file = zname

    def comprimi_e_salva(self, nome='Archivio.zip', scadenza=domani(), **kwargs):
        """
        Scorciatoia per comprimi() e effettuare il salvataggio dell'allegato in database.
        :param nome: Il nome del file da allegare (opzionale, default 'Archivio.zip').
        :param scadenza: Scadenza del file. Domani.
        :param kwargs:
        :return:
        """
        self.comprimi(nome, **kwargs)
        self.nome = nome
        self.scadenza = scadenza
        self.save()


class EAN13(Allegato):
    """
    Rappresenta una immagine di un codice EAN13 in formato PNG.
    """

    class Meta:
        proxy = True

    def genera_e_salva(self, codice, nome="Immagine.png", scadenza=None):
        generatore = GeneratoreNomeFile('allegati/')
        zname = generatore(self, nome)
        self.prepara_cartelle(MEDIA_ROOT + zname)
        pngfile = open(MEDIA_ROOT + zname, 'wb')
        writer = ImageWriter()
        writer.dpi = 400
        generate("EAN13", codice, writer=writer, output=pngfile, writer_options={
            "quiet_zone": 0.5,
            "text_distance": 0.5,
            "module_height": 5.5,
            "font_size": 13,
        })
        pngfile.close()
        self.file = zname
        self.nome = nome
        self.scadenza = scadenza
        self.save()


class PDF(Allegato):
    """
    Rappresenta un file PDF generato al volo.
    """

    class Meta:
        proxy = True

    ORIENTAMENTO_ORIZZONTALE = 'landscape'
    ORIENTAMENTO_VERTICALE = 'portrait'

    FORMATO_A4 = 'a4'
    FORMATO_CR80 = 'cr80'

    def genera_e_salva(self, nome='File.pdf', scadenza=None, corpo={}, modello='pdf_vuoto.html',
                       orientamento=ORIENTAMENTO_VERTICALE, formato=FORMATO_A4):
        """
        Genera un file PDF con i parametri specificati e salva.
        :param nome: Il nome del file PDF da salvare.
        :param scadenza: La scadenza del file PDF.
        :param corpo: Dizionario per popolare il template del corpo.
        :param modello: Il modello del file PDF.
        :param orientamento: PDF.ORIENTAMENTO_VERTICALE o PDF.ORIENTAMENTO_VERTICALE.
        :param formato: PDF.FORMATO_A4 o niente.
        :return:
        """

        scadenza = scadenza or domani()

        url = DOMPDF_ENDPOINT
        corpo.update({"timestamp": datetime.now()})
        html = get_template(modello).render(Context(corpo))
        values = {
            'paper': formato,
            'orientation': orientamento,
            'html': html
        }

        data = urllib.parse.urlencode(values)
        data = data.encode('UTF-8')
        req = urllib.request.Request(url, data)
        response = urllib.request.urlopen(req)

        generatore = GeneratoreNomeFile('allegati/')
        zname = generatore(self, nome)
        self.prepara_cartelle(MEDIA_ROOT + zname)
        pdffile = open(MEDIA_ROOT + zname, 'wb')
        pdffile.write(response.read())
        pdffile.close()

        self.file = zname
        self.nome = nome
        self.scadenza = scadenza
        self.save()


class FoglioExcel:
    """
    Rappresenta un foglio Excel.
    """

    def __init__(self, nome, intestazione):
        """
        Crea un nuovo foglio di lavoro per un documento excel.
        :param nome: Il nome del nuovo foglio di lavoro.
        :param intestazione: L'intestazione del foglio di lavoro (tupla o lista).
        """
        self.nome = nome
        self.intestazione = intestazione
        self.contenuto = []

    def aggiungi_riga(self, *riga):
        """
        Aggiunge una riga di contenuto (iterabile).
        :param riga: Tupla o lista con le colonne della riga
        """
        self.contenuto.append(riga)

    def __str__(self):
        return "<FoglioExcel: %s>" % (self.nome,)

    def __repr__(self):
        return self.__str__()


class Excel(Allegato):
    """
    Rappresenta un file Excel generato al volo.
    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Excel, self).__init__(*args, **kwargs)
        self.fogli = []

    def aggiungi_foglio(self, foglio):
        """
        Aggiunge un Foglio di lavoro di Excel al documento.
        :param foglio: Un oggetto FoglioExcel.
        """
        if not isinstance(foglio, FoglioExcel):
            raise ValueError("Il foglio Excel da aggiungere deve essere di tipo FoglioExcel.")

        self.fogli.append(foglio)

    def genera_e_salva(self, nome='File.xlsx', scadenza=None,
                       ordina_fogli=True, **kwargs):
        """
        Genera il file e lo salva su database.
        :param nome: Il nome del file da allegare (opzionale, default 'File.xlsx').
        :param scadenza: Scadenza del file. Domani.
        :param kwargs:
        :return:
        """

        scadenza = scadenza or domani()

        generatore = GeneratoreNomeFile('allegati/')
        zname = generatore(self, nome)
        self.prepara_cartelle(MEDIA_ROOT + zname)

        workbook = xlsxwriter.Workbook(MEDIA_ROOT + zname)
        bold = workbook.add_format({'bold': True})

        for foglio in [x for x in self.fogli]:  # Per ogni foglio

            # Aggiunge il foglio
            worksheet = workbook.add_worksheet(foglio.nome)

            # Aggiunge l'intestazione
            for col, testo in enumerate(foglio.intestazione):
                worksheet.write(0, col, str(testo), bold)

            # Aggiunge il contenuto
            for riga, colonne in enumerate(foglio.contenuto):
                riga += 1  # Indice shiftato per intestazione
                for colonna, testo in enumerate(colonne):
                    if isinstance(testo, datetime):
                        testo = testo.strftime("%d/%m/%Y %H:%M")
                    if isinstance(testo, date):
                        testo = testo.strftime("%d/%m/%Y")
                    if testo == ", ":  # Rimuove campi ', '
                        testo = ""
                    worksheet.write(riga, colonna, str(testo))

        if ordina_fogli:
            workbook.worksheets_objs.sort(key=lambda x: x.name)
        workbook.close()

        self.file = zname
        self.nome = nome
        self.scadenza = scadenza
        self.save()
