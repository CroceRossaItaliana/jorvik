from datetime import timedelta
from django.core.urlresolvers import reverse
from django.test import TestCase

from anagrafica.costanti import TERRITORIALE
from base.utils import poco_fa
from base.utils_tests import crea_persona, crea_sede, crea_appartenenza, email_fittizzia, crea_utenza
from donazioni.models import Etichetta, Campagna, Donazione
from donazioni.tests.utils import crea_campagna, aggiungi_responsabile_campagna


class TestVisteCampagne(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.presidente = crea_persona()
        cls.responsabile_campagna = crea_persona()
        cls.sede = crea_sede(cls.presidente, estensione=TERRITORIALE)
        crea_appartenenza(cls.responsabile_campagna, cls.sede)
        crea_utenza(cls.presidente, email=email_fittizzia())
        crea_utenza(cls.responsabile_campagna, email=email_fittizzia())

    def test_presidente_permessi(self):
        self.client.login(username=self.presidente.utenza.email, password='prova')
        response = self.client.get('/utente/')
        self.assertContains(response, '<a href="/donazioni/" class="grassetto">')
        response = self.client.get(reverse('donazioni_campagne_nuova'))
        self.assertEqual(response.status_code, 200)

    def test_responsabile_permessi(self):
        self.client.login(username=self.responsabile_campagna.utenza.email, password='prova')
        response = self.client.get('/utente/')
        self.assertNotContains(response, '<a href="/donazioni/" class="grassetto">')
        nome_campagna = 'Test Campagna'
        campagna = crea_campagna(self.sede, nome=nome_campagna)
        aggiungi_responsabile_campagna(campagna, self.responsabile_campagna)
        response = self.client.get('/utente/')
        self.assertContains(response, '<a href="/donazioni/" class="grassetto">')
        response = self.client.get(reverse('donazioni_campagne_nuova'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/errore/permessi/')

    def test_crea_campagna(self):
        self.client.login(username=self.presidente.utenza.email, password='prova')
        data = {'inizio': poco_fa(), 'fine': poco_fa() + timedelta(days=20),
                'organizzatore': self.sede.id,
                'nome': 'Nuova campagna test viste', 'descrizione': '<p>test viste</p>'}
        response = self.client.post(reverse('donazioni_campagne_nuova'), data=data)
        campagna = Campagna.objects.first()
        etichetta_creata = Etichetta.objects.first()
        self.assertTrue(etichetta_creata.default)
        self.assertIn(etichetta_creata, campagna.etichette.all())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('donazioni_campagna_responsabili', args=(campagna.id,)))


class TestVisteDonazioni(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.presidente = crea_persona()
        cls.responsabile_campagna = crea_persona()
        cls.sede = crea_sede(cls.presidente, estensione=TERRITORIALE)
        crea_appartenenza(cls.responsabile_campagna, cls.sede)
        crea_utenza(cls.presidente, email=email_fittizzia())
        crea_utenza(cls.responsabile_campagna, email=email_fittizzia())
        cls.campagna = crea_campagna(cls.sede, nome='Campagna test')
        aggiungi_responsabile_campagna(cls.campagna, cls.responsabile_campagna)

    def test_aggiungi_donazione_senza_dati_donatore(self):
        self.client.login(username=self.responsabile_campagna.utenza.email, password='prova')
        data = {'modalita': 'C', 'importo': 150.0,
                'campagna': self.campagna.id,
                'codice_transazione': 'AXYYGGGTTSADDXXX10003231010113',
                }
        response = self.client.post(reverse('donazioni_campagne_nuova_donazione', args=(self.campagna.id,)), data=data)
        self.assertEqual(response.url, reverse('donazioni_campagna', args=(self.campagna.id,)))
        donazione = Donazione.objects.filter(campagna=self.campagna).first()
        self.assertEqual(donazione.campagna, self.campagna)
        self.assertEqual(donazione.importo, 150.0)
