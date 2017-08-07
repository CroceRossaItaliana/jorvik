import datetime
import random
import string

from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.test import TestCase

from anagrafica.models import Delega
from anagrafica.permessi.applicazioni import PRESIDENTE, UFFICIO_SOCI
from autenticazione.utils_test import TestFunzionale
from base.files import Zip
from base.utils_tests import crea_persona, crea_persona_sede_appartenenza

from articoli.models import Articolo, ArticoloSegmento


def parola_casuale(lunghezza):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(lunghezza))


class ArticoliTests(TestCase):

    def test_titolo_lungo(self):

        articolo = Articolo.objects.create(
            titolo='Corso di aggiornamento per coordinatori attività di emergenza',
            corpo=parola_casuale(3000),
            data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
        )

        self.assertEqual(articolo.corpo[:Articolo.DIMENSIONE_ESTRATTO], articolo.estratto)
        self.assertFalse(articolo.termina)
        self.assertEqual(articolo.slug, 'corso-di-aggiornamento-per-coordinatori-attivita-di-emergenza')

    def test_slug(self):
        articolo_1 = Articolo.objects.create(
            titolo='corso',
            corpo=parola_casuale(3000),
            data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
        )
        articolo_2 = Articolo.objects.create(
            titolo='corso',
            corpo=parola_casuale(3000),
            data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
        )

        self.assertNotEqual(articolo_1.slug, articolo_2.slug)

    def test_articolo(self):

        CONTENUTO_1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
        NOME_1 = 'Test1.txt'
        CONTENUTO_2 = "Donec tempus nisi eu enim consequat, non scelerisque nisi accumsan.\n"
        NOME_2 = 'Test/Test2.txt'

        volontario, _, _ = crea_persona_sede_appartenenza()
        presidente = crea_persona()
        presidente.save()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        delega_presidente_in_corso = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_in_corso.save()

        articolo = Articolo.objects.create(
                titolo='Titolo 1',
                corpo=parola_casuale(3000),
                data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
            )

        self.assertEqual(articolo.corpo[:Articolo.DIMENSIONE_ESTRATTO], articolo.estratto)
        self.assertFalse(articolo.termina)

        articolo2 = Articolo.objects.create(
                titolo='Titolo 2',
                corpo='Testo random',
                estratto='estratto qualsiasi',
                data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
                data_fine_pubblicazione=datetime.datetime.now() + datetime.timedelta(days=5),
                stato=Articolo.PUBBLICATO
            )

        segmento_presidenti_no_filtri = ArticoloSegmento.objects.create(
            segmento='I',
            articolo=articolo2,
        )

        self.assertNotEqual(articolo2.corpo, articolo2.estratto)
        self.assertEqual(articolo2.estratto, 'estratto qualsiasi')
        self.assertTrue(articolo2.termina)

        articolo3 = Articolo.objects.create(
                titolo='Titolo 3',
                corpo='Testo qualsiasi',
                estratto='estratto random',
                data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
                stato=Articolo.PUBBLICATO
            )

        segmento_volontari_no_filtri = ArticoloSegmento.objects.create(
            segmento='B',
            articolo=articolo3
        )

        z = Zip(oggetto=articolo3)
        f1 = NamedTemporaryFile(delete=False, mode='wt')
        f1.write(CONTENUTO_1)
        f1.close()
        z.aggiungi_file(f1.name, NOME_1)
        z.comprimi_e_salva(nome='TestZip.zip')

        self.assertEqual(1, articolo3.allegati.all().count())
        self.assertIn(z, articolo3.allegati.all())

        articolo4 = Articolo.objects.create(
                titolo='Titolo 4',
                corpo='Testo qualsiasi 2',
                estratto='estratto random 2',
                data_inizio_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=5),
                data_fine_pubblicazione=datetime.datetime.now() - datetime.timedelta(days=2),
                stato=Articolo.PUBBLICATO
            )

        pubblicati = Articolo.objects.pubblicati()
        bozze = Articolo.objects.bozze()
        self.assertEqual(pubblicati.count(), 2)
        self.assertEqual(bozze.count(), 1)
        self.assertIn(articolo, bozze)
        self.assertNotIn(articolo, pubblicati)
        self.assertNotIn(articolo2, bozze)
        self.assertIn(articolo2, pubblicati)
        self.assertNotIn(articolo3, bozze)
        self.assertIn(articolo3, pubblicati)
        self.assertNotIn(articolo4, bozze)
        self.assertNotIn(articolo4, pubblicati)

        segmenti_volontario = ArticoloSegmento.objects.all().filtra_per_segmenti(volontario)
        articoli_volontario = segmenti_volontario.oggetti_collegati()
        self.assertNotIn(articolo2, articoli_volontario)
        self.assertIn(articolo3, articoli_volontario)

        segmenti_presidente = ArticoloSegmento.objects.all().filtra_per_segmenti(presidente)
        articoli_presidente = segmenti_presidente.oggetti_collegati()
        self.assertIn(articolo2, articoli_presidente)
        self.assertIn(articolo3, articoli_presidente)


class TestFunzionaleArticoli(TestFunzionale):

    def test_lista_articoli_vuota(self):
        persona = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza()
        sessione_persona = self.sessione_utente(persona=persona)
        sessione_persona.visit("%s%s" % (self.live_server_url, reverse('lista_articoli')))
        self.assertTrue(sessione_persona.is_text_present('Non è stato trovato alcun articolo'))

    def test_lista_articoli(self):
        articolo = Articolo.objects.create(
            titolo='Titolo 1981',
            corpo='Testo random 1',
            estratto='qualcosa',
            data_inizio_pubblicazione='1981-12-10',
            stato=Articolo.PUBBLICATO
        )
        articolo2 = Articolo.objects.create(
            titolo='Titolo primo 1980',
            corpo='Testo random 2',
            estratto='un pezzo',
            data_inizio_pubblicazione='1980-06-10',
            stato=Articolo.PUBBLICATO
        )
        articolo3 = Articolo.objects.create(
            titolo='Titolo secondo 1980',
            corpo='Testo random 3',
            estratto='una parte',
            data_inizio_pubblicazione='1980-12-10',
            stato=Articolo.PUBBLICATO
        )
        persona = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza()
        sessione_persona = self.sessione_utente(persona=persona)
        sessione_persona.visit("%s%s" % (self.live_server_url, reverse('lista_articoli')))
        self.assertFalse(sessione_persona.is_text_present('Non è stato trovato alcun articolo'))
        self.assertTrue(sessione_persona.is_text_present(articolo.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo3.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo3.estratto))
        self.assertEqual(3, len(sessione_persona.find_by_css('.panel.articolo-lista')))
        sessione_persona.fill('q', 'primo')
        sessione_persona.find_by_xpath('//button[@type="submit"]').first.click()
        self.assertEqual(1, len(sessione_persona.find_by_css('.panel.articolo-lista')))
        self.assertFalse(sessione_persona.is_text_present(articolo.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.estratto))
        self.assertFalse(sessione_persona.is_text_present(articolo3.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo3.estratto))
        sessione_persona.find_by_xpath('//select[@name="anno"]//option[@value="1980"]').first.click()
        sessione_persona.find_by_xpath('//button[@type="submit"]').first.click()
        self.assertEqual(1, len(sessione_persona.find_by_css('.panel.articolo-lista')))
        self.assertFalse(sessione_persona.is_text_present(articolo.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.estratto))
        self.assertFalse(sessione_persona.is_text_present(articolo3.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo3.estratto))
        sessione_persona.fill('q', '')
        sessione_persona.find_by_xpath('//select[@name="anno"]//option[@value="1980"]').first.click()
        sessione_persona.find_by_xpath('//button[@type="submit"]').first.click()
        self.assertEqual(2, len(sessione_persona.find_by_css('.panel.articolo-lista')))
        self.assertFalse(sessione_persona.is_text_present(articolo.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo3.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo3.estratto))
        sessione_persona.find_by_xpath('//select[@name="anno"]//option[@value="1980"]').first.click()
        sessione_persona.find_by_xpath('//select[@name="mese"]//option[@value=6]').first.click()
        sessione_persona.find_by_xpath('//button[@type="submit"]').first.click()
        self.assertEqual(1, len(sessione_persona.find_by_css('.panel.articolo-lista')))
        self.assertFalse(sessione_persona.is_text_present(articolo.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo.estratto))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.estratto))
        self.assertFalse(sessione_persona.is_text_present(articolo3.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo3.estratto))
        sessione_persona.find_link_by_partial_text('Continua a leggere').first.click()
        self.assertFalse(sessione_persona.is_text_present(articolo.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo.corpo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present(articolo2.corpo))
        self.assertFalse(sessione_persona.is_text_present(articolo3.titolo))
        self.assertFalse(sessione_persona.is_text_present(articolo3.corpo))
        self.assertTrue(sessione_persona.is_text_present('Letture'))

    def test_dettaglio_articoli_pubblici(self):
        articolo = Articolo.objects.create(
            titolo='Titolo 1981',
            corpo='Testo random',
            estratto='qualcosa',
            data_inizio_pubblicazione='1981-12-10',
            stato=Articolo.PUBBLICATO
        )
        articolo2 = Articolo.objects.create(
            titolo='Titolo primo 1980',
            corpo='Testo random 2',
            estratto='un pezzo',
            data_inizio_pubblicazione='1980-06-10',
            stato=Articolo.PUBBLICATO
        )
        segmento_presidenti_no_filtri = ArticoloSegmento.objects.create(
            segmento='I',
            articolo=articolo2,
        )
        sessione_persona = self.sessione_anonimo()
        sessione_persona.visit("%s%s" % (
            self.live_server_url, reverse('dettaglio_articolo', kwargs={
                'articolo_slug': articolo.slug
            })
        ))
        self.assertTrue(sessione_persona.is_text_present(articolo.titolo))
        settings.DEBUG = True

        sessione_persona.visit("%s%s" % (
            self.live_server_url, reverse('dettaglio_articolo', kwargs={
                'articolo_slug': articolo2.slug
            })
        ))
        self.assertFalse(sessione_persona.is_text_present(articolo2.titolo))
        self.assertTrue(sessione_persona.is_text_present('Accedi a Gaia'))

    def test_dettaglio_articoli_protected(self):
        articolo = Articolo.objects.create(
            titolo='Titolo 1981',
            corpo='Testo random',
            estratto='qualcosa',
            data_inizio_pubblicazione='1981-12-10',
            stato=Articolo.PUBBLICATO
        )
        segmento_presidenti_no_filtri = ArticoloSegmento.objects.create(
            segmento='I',
            articolo=articolo,
        )
        normale = crea_persona()
        normale.save()
        normale, sede, _ = crea_persona_sede_appartenenza(normale)
        delega_us = Delega(
            persona=normale,
            tipo=UFFICIO_SOCI,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_us.save()
        sessione_persona = self.sessione_utente(persona=normale)
        sessione_persona.visit("%s%s" % (
            self.live_server_url, reverse('dettaglio_articolo', kwargs={
                'articolo_slug': articolo.slug
            })
        ))
        self.assertTrue(sessione_persona.is_text_present('Accesso Negato, siamo spiacenti'))

    def test_dettaglio_articoli_privati(self):
        articolo = Articolo.objects.create(
            titolo='Titolo 1981',
            corpo='Testo random',
            estratto='qualcosa',
            data_inizio_pubblicazione='1981-12-10',
            stato=Articolo.PUBBLICATO
        )
        presidente = crea_persona()
        presidente.save()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        delega_presidente_in_corso = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_in_corso.save()
        sessione_persona = self.sessione_utente(persona=presidente)
        sessione_persona.visit("%s%s" % (
            self.live_server_url, reverse('dettaglio_articolo', kwargs={
                'articolo_slug': articolo.slug
            })
        ))
        self.assertTrue(sessione_persona.is_text_present(articolo.titolo))
