import os
from zipfile import ZipFile
from django.core.files import File
from base.models import Allegato
from base.stringhe import domani, GeneratoreNomeFile
from jorvik.settings import MEDIA_ROOT
from io import StringIO

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
