import os

from unittest import skipIf
from zipfile import ZipFile
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from anagrafica.models import Persona
from autenticazione.utils_test import TestFunzionale
from base.files import Zip
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_area_attivita
from jorvik.settings import GOOGLE_KEY


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


class TestFunzionaleBase(TestFunzionale):

    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    def test_ricerca_posizione(self):

        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        area, attivita = crea_area_attivita(sede=sede)

        sessione_presidente = self.sessione_utente(persona=presidente)
        sessione_presidente.visit("%s%s" % (self.live_server_url,
                                            attivita.url_modifica))

        with sessione_presidente.get_iframe(0) as iframe:

            iframe.fill('indirizzo', 'via etnea 353')
            iframe.fill('comune', 'ct')
            iframe.fill('provincia', 'ctnia')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            self.assertTrue(
                iframe.is_text_present("Via Etnea, 353, 95125 Catania CT, Italia"),
                msg="Indirizzo trovato correttamente"
            )

            iframe.find_by_xpath("//button[@value='Via Etnea, 353, 95125 Catania CT, Italia']").first.click()

            self.assertTrue(
                iframe.is_text_present("Via Etnea, 353, 95125 Catania CT, Italia", wait_time=5),
                msg="Indirizzo salvato correttamente"
            )

    def test_recupero_password_skip_captcha(self):
        sessione = self.sessione_anonimo()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        sessione.fill('codice_fiscale', 'via etnea 353')
        sessione.fill('email', 'prova@spalletti.it')
        sessione.find_by_xpath("//button[@type='submit']").first.click()

        self.assertTrue(sessione.is_text_present('Questo campo è obbligatorio.'))

    def test_recupero_password_cf_non_esiste(self):
        sessione = self.sessione_anonimo()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        # questo server a permettere di interagire con il campo nascosto del captcha
        sessione.execute_script(
            'document.getElementById("g-recaptcha-response").style.display = "block";'
        )
        sessione.fill('codice_fiscale', 'CFERRATO')
        sessione.fill('email', 'prova@spalletti.it')
        sessione.fill('g-recaptcha-response', 'PASSED')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        self.assertTrue(sessione.is_text_present('Account non esistente'))
        self.assertTrue(sessione.is_text_present('Registrati'))

    def test_recupero_password_persona_non_utente(self):

        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        sessione = self.sessione_anonimo()

        # test con codice fiscale non associato ad utenza per persona associata a sede
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))
        # questo server a permettere di interagire con il campo nascosto del captcha
        sessione.execute_script(
            'document.getElementById("g-recaptcha-response").style.display = "block";'
        )
        sessione.fill('codice_fiscale', persona.codice_fiscale)
        sessione.fill('email', 'prova@spalletti.it')
        sessione.fill('g-recaptcha-response', 'PASSED')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        self.assertTrue(sessione.is_text_present('Nessuna utenza'))
        self.assertTrue(sessione.is_text_present('Chiedi al tuo Ufficio Soci'))
        self.assertTrue(sessione.is_text_present('{} (Presidente)'.format(presidente.nome_completo)))

        # test con codice fiscale non associato ad utenza per persona non associata a sede
        persona_senza_sede = crea_persona()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))
        # questo server a permettere di interagire con il campo nascosto del captcha
        sessione.execute_script(
            'document.getElementById("g-recaptcha-response").style.display = "block";'
        )
        sessione.fill('codice_fiscale', persona_senza_sede.codice_fiscale)
        sessione.fill('email', 'prova@spalletti.it')
        sessione.fill('g-recaptcha-response', 'PASSED')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        sessione.screenshot()

        self.assertTrue(sessione.is_text_present('Nessuna utenza'))
        self.assertTrue(sessione.is_text_present('Supporto di Gaia'))
