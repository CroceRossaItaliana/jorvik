import os
from datetime import datetime
from zipfile import ZipFile
from django.core.files import File
from django.template import Context
from django.template.loader import get_template

from base.models import Allegato
from base.stringhe import domani, GeneratoreNomeFile
from jorvik.settings import MEDIA_ROOT, DOMPDF_ENDPOINT
from io import StringIO
import urllib

__author__ = 'alfioemanuele'


class Zip(Allegato):
    """
    Rappresenta un file ZIP generato al volo.
    """

    class Meta:
        proxy = True

    _file_in_attesa = []

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


class PDF(Allegato):
    """
    Rappresenta un file PDF generato al volo.
    """

    class Meta:
        proxy = True

    ORIENTAMENTO_ORIZZONTALE = 'landscape'
    ORIENTAMENTO_VERTICALE = 'portrait'

    FORMATO_A4 = 'a4'

    def genera_e_salva(self, nome='File.pdf', scadenza=domani(), corpo={}, modello='pdf_vuoto.html',
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
