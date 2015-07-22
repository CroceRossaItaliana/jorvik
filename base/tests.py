from zipfile import ZipFile
from django.core.files.temp import NamedTemporaryFile
from django.test import TestCase
from anagrafica.models import Persona
from base.files import Zip


class TestBase(TestCase):

    CONTENUTO_1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
    NOME_1 = 'Test1.txt'
    CONTENUTO_2 = "Donec tempus nisi eu enim consequat, non scelerisque nisi accumsan.\n"
    NOME_2 = 'Test/Test2.txt'

    def test_zip(self):

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJD2",
            data_nascita="1994-2-5"
        )
        p.save()

        z = Zip(oggetto=p)

        # Crea file 1
        f1 = NamedTemporaryFile(delete=False, mode='wt')
        f1.write(self.CONTENUTO_1)
        f1.close()

        # Crea file 2
        f2 = NamedTemporaryFile(delete=False, mode='wt')
        f2.write(self.CONTENUTO_2)
        f2.close()

        # Genera ZIP file
        z.aggiungi_file(f1.name, self.NOME_1)
        z.aggiungi_file(f2.name, self.NOME_2)
        z.comprimi_e_salva(nome='TestZip.zip')

        # Apri e verifica ZIP
        z = Zip.objects.get(nome='TestZip.zip')

        with ZipFile(z.file.path, 'r') as zip:

            self.assertIsNone(
                zip.testzip(),
                msg="Il file Zip non e' corrotto"
            )

            r1 = zip.open(self.NOME_1)
            self.assertTrue(
                r1.read().decode() == self.CONTENUTO_1,
                msg="Il contenuto del primo file coincide"
            )

            r2 = zip.open(self.NOME_2)
            self.assertTrue(
                r2.read().decode() == self.CONTENUTO_2,
                msg="Il contenuto del secondo file coincide"
            )

            zip.close()

        self.assertTrue(
            p.allegati.all(),
            msg="Allegato associato correttamente alla persona"
        )
