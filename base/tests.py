import datetime
import os
import tempfile

from unittest import skipIf
from unittest.mock import patch
from zipfile import ZipFile
from django.contrib.auth.tokens import default_token_generator
import django.core.files
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from articoli.models import Articolo
from anagrafica.models import Persona
from autenticazione.utils_test import TestFunzionale
from base.files import Zip
from base.geo import Locazione
from base.utils import UpperCaseCharField
from base.utils_tests import crea_appartenenza, crea_persona_sede_appartenenza, crea_persona, crea_area_attivita, crea_utenza
from gestione_file.models import Documento
from jorvik.settings import GOOGLE_KEY
from filer.models import Folder
from filer.tests import create_image

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


class TestGeo(TestCase):
    posto_google = [
        {'place_id': 'ChIJ4ZrMcgdhLxMR7F_Z1sLKCOA',
         'formatted_address': 'Via Toscana, 12, 00187 Roma, Italia',
         'geometry': {'location': {'lng': 0, 'lat': 0},
                      'location_type': 'ROOFTOP', 'viewport':
                          {'northeast': {'lng': 12.4929659802915, 'lat': 41.90993408029149},
                           'southwest': {'lng': 12.4902680197085, 'lat': 41.90723611970849}}},
         'types': ['street_address'], 'address_components': [
            {'short_name': '12', 'long_name': '12', 'types': ['street_number']},
            {'short_name': 'Via Toscana', 'long_name': 'Via Toscana', 'types': ['route']},
            {'short_name': 'Roma', 'long_name': 'Roma', 'types': ['locality', 'political']},
            {'short_name': 'Roma', 'long_name': 'Roma', 'types': ['administrative_area_level_3', 'political']},
            {'short_name': 'RM', 'long_name': 'Città Metropolitana di Roma', 'types': ['administrative_area_level_2', 'political']},
            {'short_name': 'Lazio', 'long_name': 'Lazio', 'types': ['administrative_area_level_1', 'political']},
            {'short_name': 'IT', 'long_name': 'Italia', 'types': ['country', 'political']},
            {'short_name': '00187', 'long_name': '00187', 'types': ['postal_code']}]}]

    posto_senza_coord = [
        {'place_id': 'ChIJ4ZrMcgdhLxMR7F_Z1sLKCOA',
         'formatted_address': 'Via Toscana, 12, 00187 Roma, Italia',
         'geometry': {'location': '',
                      'location_type': 'ROOFTOP', 'viewport':
                          {'northeast': {'lng': 12.4929659802915, 'lat': 41.90993408029149},
                           'southwest': {'lng': 12.4902680197085, 'lat': 41.90723611970849}}},
         'types': ['street_address'], 'address_components': [
            {'short_name': '12', 'long_name': '12', 'types': ['street_number']},
            {'short_name': 'Via Toscana', 'long_name': 'Via Toscana', 'types': ['route']},
            {'short_name': 'Roma', 'long_name': 'Roma', 'types': ['locality', 'political']},
            {'short_name': 'Roma', 'long_name': 'Roma', 'types': ['administrative_area_level_3', 'political']},
            {'short_name': 'RM', 'long_name': 'Città Metropolitana di Roma', 'types': ['administrative_area_level_2', 'political']},
            {'short_name': 'Lazio', 'long_name': 'Lazio', 'types': ['administrative_area_level_1', 'political']},
            {'short_name': 'IT', 'long_name': 'Italia', 'types': ['country', 'political']},
            {'short_name': '00187', 'long_name': '00187', 'types': ['postal_code']}]}]

    posti_africa = [
        [
            [{'partial_match': True, 'geometry': {'location_type': 'GEOMETRIC_CENTER',
                                                  'viewport': {'southwest': {'lng': -1.622701, 'lat': 6.6697722},
                                                               'northeast': {'lng': -1.6176442,
                                                                             'lat': 6.680420799999999}},
                                                  'location': {'lng': -1.6204888, 'lat': 6.6748961},
                                                  'bounds': {'southwest': {'lng': -1.622701, 'lat': 6.6697722},
                                                             'northeast': {'lng': -1.6176442,
                                                                           'lat': 6.680420799999999}}},
              'address_components': [{'long_name': 'Harper Road', 'short_name': 'Harper Rd', 'types': ['route']},
                                     {'long_name': 'Adiebeba', 'short_name': 'Adiebeba',
                                      'types': ['neighborhood', 'political']},
                                     {'long_name': 'Atonsu', 'short_name': 'Atonsu',
                                      'types': ['political', 'sublocality', 'sublocality_level_1']},
                                     {'long_name': 'Kumasi', 'short_name': 'Kumasi',
                                      'types': ['locality', 'political']},
                                     {'long_name': 'Kumasi Metropolitan', 'short_name': 'Kumasi Metropolitan',
                                      'types': ['administrative_area_level_2', 'political']},
                                     {'long_name': 'Ashanti Region', 'short_name': 'Ashanti Region',
                                      'types': ['administrative_area_level_1', 'political']},
                                     {'long_name': 'Ghana', 'short_name': 'GH', 'types': ['country', 'political']}],
              'formatted_address': 'Harper Rd, Kumasi, Ghana', 'types': ['route'],
              'place_id': 'ChIJda2WAseW2w8RuCwOYKAZleY'}],
            [('Harper Rd, Kumasi, Ghana', {'lng': -1.6204888, 'lat': 6.6748961},
              {'via': 'Harper Road', 'cap': None, 'comune': 'Kumasi', 'provincia': 'Kumasi Metropolitan',
               'provincia_breve': 'Kumasi Metropolitan', 'stato': 'GH', 'civico': None, 'regione': 'Ashanti Region'})]
        ],
        [
            [{'address_components': [
                {'short_name': 'Carr. del Aeropuerto', 'long_name': 'Carretera del Aeropuerto', 'types': ['route']},
                {'short_name': 'Malabo', 'long_name': 'Malabo', 'types': ['locality', 'political']},
                {'short_name': 'Malabo', 'long_name': 'Malabo',
                 'types': ['administrative_area_level_2', 'political']},
                {'short_name': 'Bioko Norte', 'long_name': 'Bioko Norte',
                 'types': ['administrative_area_level_1', 'political']},
                {'short_name': 'GQ', 'long_name': 'Guinea Equatoriale', 'types': ['country', 'political']}],
              'types': ['route'], 'formatted_address': 'Carr. del Aeropuerto, Malabo, Guinea Equatoriale',
              'partial_match': True, 'place_id': 'ChIJK3LULCecZhARspsoYSFT9CQ', 'geometry': {
                    'bounds': {'southwest': {'lat': 3.7523714, 'lng': 8.7168735},
                               'northeast': {'lat': 3.757947499999999, 'lng': 8.7751003}},
                    'viewport': {'southwest': {'lat': 3.7523714, 'lng': 8.7168735},
                                 'northeast': {'lat': 3.757947499999999, 'lng': 8.7751003}},
                    'location_type': 'GEOMETRIC_CENTER', 'location': {'lat': 3.753685099999999, 'lng': 8.7456976}}}],
            [('Carr. del Aeropuerto, Malabo, Guinea Equatoriale', {'lat': 3.753685099999999, 'lng': 8.7456976},
              {'comune': 'Malabo', 'provincia': 'Malabo', 'regione': 'Bioko Norte', 'provincia_breve': 'Malabo',
               'civico': None, 'via': 'Carretera del Aeropuerto', 'cap': None, 'stato': 'GQ'})]
        ],
        [
            [{'geometry': {'bounds': {'northeast': {'lat': -0.7244695, 'lng': 8.767470699999999},
                                      'southwest': {'lat': -0.7461185, 'lng': 8.753189299999999}},
                           'viewport': {'northeast': {'lat': -0.7244695, 'lng': 8.767470699999999},
                                        'southwest': {'lat': -0.7461185, 'lng': 8.753189299999999}},
                           'location': {'lat': -0.7345885999999999, 'lng': 8.760486199999999},
                           'location_type': 'GEOMETRIC_CENTER'},
              'formatted_address': 'Route des Hydrocarbures, Port-Gentil, Gabon', 'address_components': [
                    {'types': ['route'], 'short_name': 'Route des Hydrocarbures',
                     'long_name': 'Route des Hydrocarbures'},
                    {'types': ['locality', 'political'], 'short_name': 'Port-Gentil', 'long_name': 'Port-Gentil'},
                    {'types': ['administrative_area_level_2', 'political'], 'short_name': 'Bendje',
                     'long_name': 'Bendje'},
                    {'types': ['administrative_area_level_1', 'political'], 'short_name': 'Ogooué-Maritime',
                     'long_name': 'Ogooué-Maritime'},
                    {'types': ['country', 'political'], 'short_name': 'GA', 'long_name': 'Gabon'}],
              'place_id': 'ChIJFSkO1Fq3gxoRauW9p1O_G_s', 'types': ['route']}],
            [('Route des Hydrocarbures, Port-Gentil, Gabon', {'lat': -0.7345885999999999, 'lng': 8.760486199999999},
              {'provincia_breve': 'Bendje', 'regione': 'Ogooué-Maritime', 'provincia': 'Bendje',
               'comune': 'Port-Gentil', 'via': 'Route des Hydrocarbures', 'stato': 'GA', 'civico': None, 'cap': None})]
        ],
    ]

    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    def test_ricerca_indirizzo(self):
        """
        Test che verifica l'effettivo funzionamento del geocoding
        """
        indirizzo_base = 'Via Toscana, 12 - 00187 Roma'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posto_google[0]['formatted_address'])
        self.assertEqual(len(indirizzo[0][1]), 2)
        self.assertEqual(indirizzo[0][2]['provincia_breve'], 'RM')

    @patch('base.geo.googlemaps.Client.geocode', return_value=posto_google)
    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    def test_ricerca_indirizzo_senza_coordinate(self, mocked):
        """
        Test che verifica il valore ritornato se le coordinate non sono valide
        """
        indirizzo_base = 'Via Toscana, 12 - 00187 Roma'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posto_google[0]['formatted_address'])
        self.assertEqual(indirizzo[0][1], '0')
        self.assertEqual(indirizzo[0][2]['provincia_breve'], 'RM')

    @patch('base.geo.googlemaps.Client.geocode', return_value=posto_senza_coord)
    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    def test_ricerca_indirizzo_con_attributi_errati(self, mocked):
        """
        Test che verifica la robustezza della logica di gestione del geocoding
        """
        indirizzo_base = 'Via Toscana, 12 - 00187 Roma'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posto_google[0]['formatted_address'])
        self.assertEqual(indirizzo[0][1], '0')
        self.assertEqual(indirizzo[0][2]['provincia_breve'], 'RM')

    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    def test_ricerca_indirizzi_africa(self):
        """
        Test che verifica la disponibilità di sedi in africa
        """
        # Est di Greenwitch, Nord dell'equatore
        indirizzo_base = 'Harper Road 40, Kumasi, Ghana'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posti_africa[0][0][0]['formatted_address'])
        self.assertEqual(indirizzo[0][1], self.posti_africa[0][0][0]['geometry']['location'])

        # Ovest di Greenwitch, Nord dell'equatore
        indirizzo_base = 'Carrettera del Aeropuerto, Malabo, Guinea Equatoriale'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posti_africa[1][0][0]['formatted_address'])
        self.assertEqual(indirizzo[0][1], self.posti_africa[1][0][0]['geometry']['location'])

        # Ovest di Greenwitch, Sud dell'equatore
        indirizzo_base = 'Route des Hydrocarbures, Port Gentil, Gabon'
        indirizzo = Locazione.cerca(indirizzo_base)
        self.assertEqual(len(indirizzo[0]), 3)
        self.assertEqual(indirizzo[0][0], self.posti_africa[2][0][0]['formatted_address'])
        self.assertEqual(indirizzo[0][1], self.posti_africa[2][0][0]['geometry']['location'])

        # Est di Greenwitch, Sud dell'equatore
        # Non c'è nulla :D


class TestUtils(TestBase):

    def test_uppercasecharfield(self):
        field_stub = UpperCaseCharField()
        self.assertEqual(field_stub.to_python(None), None)
        self.assertEqual(field_stub.to_python(1), 1)
        self.assertEqual(field_stub.to_python(''), '')
        self.assertEqual(field_stub.to_python('testo minuscolo'), 'TESTO MINUSCOLO')
        self.assertEqual(field_stub.to_python(False), False)


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
        sessione.fill('email', 'prova@testprova.it')
        sessione.find_by_xpath("//button[@type='submit']").first.click()

        self.assertTrue(sessione.is_text_present('Questo campo è obbligatorio.'))

    @patch('base.forms.NoReCaptchaField.clean', return_value='PASSED')
    def test_recupero_password_cf_non_esiste(self, mocked):
        sessione = self.sessione_anonimo()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        sessione.fill('codice_fiscale', 'CFERRATO')
        sessione.fill('email', 'prova@testprova.it')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        self.assertTrue(sessione.is_text_present('Siamo spiacenti, non ci risulta alcuna persona con questo codice fiscale (CFERRATO)'))
        self.assertTrue(sessione.is_text_present('registrati come aspirante Volontario.'))

    @patch('base.forms.NoReCaptchaField.clean', return_value='PASSED')
    def test_recupero_password_persona_non_utente(self, mocked):

        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        sessione = self.sessione_anonimo()

        # test con codice fiscale non associato ad utenza per persona associata a sede
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        sessione.fill('codice_fiscale', persona.codice_fiscale)
        sessione.fill('email', 'prova@testprova.it')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        self.assertTrue(sessione.is_text_present('Nessuna utenza'))
        self.assertTrue(sessione.is_text_present('Chiedi al tuo Ufficio Soci'))
        self.assertTrue(sessione.is_text_present('{} (Presidente)'.format(presidente.nome_completo)))

        # test con codice fiscale non associato ad utenza per persona non associata a sede
        persona_senza_sede = crea_persona()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        sessione.fill('codice_fiscale', persona_senza_sede.codice_fiscale)
        sessione.fill('email', 'prova@spalletti.it')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()

        sessione.screenshot()

        self.assertTrue(sessione.is_text_present('Nessuna utenza'))
        self.assertTrue(sessione.is_text_present('Supporto di Gaia'))

    @patch('base.forms.NoReCaptchaField.clean', return_value='PASSED')
    def test_recupero_password_email_errata(self, mocked):
        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        persona_in_sede = crea_persona()
        utenza_persona_in_sede = crea_utenza(persona_in_sede)
        appartenenza_persona_in_sede = crea_appartenenza(persona, sede)
        sessione = self.sessione_anonimo()

        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))

        sessione.fill('codice_fiscale', persona_in_sede.codice_fiscale)
        sessione.fill('email', 'prova@spalletti.it')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()
        self.assertTrue(sessione.is_text_present('ma NON con questo indirizzo e-mail (prova@spalletti.it)'))
        self.assertTrue(sessione.is_text_present('Supporto di Gaia'))

    @patch('base.forms.NoReCaptchaField.clean', return_value='PASSED')
    def test_recupero_password_corretto(self, mocked):
        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        persona_in_sede = crea_persona()
        utenza_persona_in_sede = crea_utenza(persona_in_sede)
        appartenenza_persona_in_sede = crea_appartenenza(persona, sede)
        sessione = self.sessione_anonimo()

        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password')))
        sessione.fill('codice_fiscale', persona_in_sede.codice_fiscale)
        sessione.fill('email', utenza_persona_in_sede.email)
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()
        self.assertTrue(sessione.is_text_present('Ti abbiamo inviato le istruzioni per cambiare la tua password tramite e-mail'))

    def test_recupero_password_link_non_valido(self):
        sessione = self.sessione_anonimo()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password_conferma',  kwargs={ 'uidb64': 'AB', 'token': 'cde-fghilmnopqrstuvz1234'})))
        self.assertTrue(sessione.is_text_present('Il collegamento che hai seguito non è più valido'))
        self.assertTrue(sessione.is_text_present('Se sei assolutamente certo/a di non aver richiesto che la tua password venisse reimpostata, il tuo account di posta potrebbe essere stato compromesso: contatta immediatamente il tuo Ufficio Soci ed il supporto tecnico del tuo fornitore del servizio di posta elettronica.'))

    def test_recupero_password_link_valido(self):
        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)
        persona_in_sede = crea_persona()
        utenza_persona_in_sede = crea_utenza(persona_in_sede)
        appartenenza_persona_in_sede = crea_appartenenza(persona, sede)
        uid = urlsafe_base64_encode(force_bytes(utenza_persona_in_sede.pk))
        reset_pw_link = default_token_generator.make_token(utenza_persona_in_sede)
        sessione = self.sessione_anonimo()
        sessione.visit("%s%s" % (self.live_server_url, reverse('recupera_password_conferma',  kwargs={ 'uidb64': uid, 'token': reset_pw_link})))
        sessione.fill('new_password1', 'new_password')
        sessione.fill('new_password2', 'new_password')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()
        self.assertTrue(sessione.is_text_present('La tua nuova password è stata impostata'))
        sessione.visit("%s%s" % (self.live_server_url, '/login/'))
        sessione.fill('auth-username', utenza_persona_in_sede.email)
        sessione.fill('auth-password', 'new_password')
        sessione.find_by_css('.btn.btn-block.btn-primary').first.click()
        testo_personalizzato = 'Ciao, {0}'.format(persona_in_sede.nome)
        self.assertTrue(sessione.is_text_present(testo_personalizzato))
