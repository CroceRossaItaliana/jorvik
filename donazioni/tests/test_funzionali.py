from datetime import timedelta

from django.core.urlresolvers import reverse

from anagrafica.models import Persona, Appartenenza
from anagrafica.permessi.applicazioni import DELEGATO_CAMPAGNE, RESPONSABILE_CAMPAGNA
from autenticazione.models import Utenza
from autenticazione.utils_test import TestFunzionale
from base.utils import poco_fa
from base.utils_tests import crea_sede, crea_persona, crea_delega, crea_appartenenza, crea_utenza
from donazioni.models import Campagna, Etichetta
from donazioni.tests.utils import crea_campagna


class TestFunzionaliCampagneEtichette(TestFunzionale):
    def setUp(self):
        super(TestFunzionale, self).setUp()
        self.presidente = crea_persona()
        self.sede = crea_sede(self.presidente)
        self.delegato = crea_persona()
        crea_utenza(self.delegato, email='delegato@cri.it')
        crea_appartenenza(self.delegato, self.sede)
        crea_delega(self.delegato, self.sede, DELEGATO_CAMPAGNE)

    def tearDown(self):
        super(TestFunzionale, self).tearDown()
        Appartenenza.objects.all().delete()
        Utenza.objects.all().delete()
        Persona.objects.all().delete()

    def test_delegato_crea_campagna(self):

        url_crea_campagna = '{}{}'.format(self.live_server_url, reverse('donazioni_campagne_nuova'))
        sessione_delegato = self.sessione_utente(persona=self.delegato)
        sessione_delegato.visit(url_crea_campagna)
        dati_campagna = {'inizio': poco_fa().strftime("%d/%m/%Y %H:%M"),
                         'fine': (poco_fa() + timedelta(days=30)).strftime("%d/%m/%Y %H:%M"),
                         'nome': 'test campagna'}
        sessione_delegato.fill_form(dati_campagna)
        for k in sessione_delegato.type('organizzatore-autocomplete', self.sede.nome, slowly=True):
            try:
                sessione_delegato.find_by_xpath("//span[@data-value='{}']".format(self.sede.id)).first.click()
            except:
                pass
            else:
                break
        sessione_delegato.find_by_xpath("//button[@type='submit']").first.click()
        campagna = Campagna.objects.first()
        self.assertEqual(sessione_delegato.url, '{}{}'.format(self.live_server_url,
                                                              reverse('donazioni_campagna_responsabili', args=(campagna.id,))))
        self.assertTrue(sessione_delegato.is_text_present('Seleziona almeno un Responsabile per la campagna'))

    def test_delegato_crea_etichetta(self):
        url_crea_etichetta = '{}{}'.format(self.live_server_url,
                                           reverse('donazioni_etichette_nuova'))

        sessione_delegato = self.sessione_utente(persona=self.delegato)
        sessione_delegato.visit(url_crea_etichetta)
        sessione_delegato.fill('slug', 'test-etichetta')
        for k in sessione_delegato.type('comitato-autocomplete', self.sede.nome, slowly=True):
            try:
                sessione_delegato.find_by_xpath("//span[@data-value='{}']".format(self.sede.id)).first.click()
            except:
                pass
            else:
                break
        sessione_delegato.find_by_xpath("//button[@type='submit']").first.click()
        etichetta = Etichetta.objects.first()
        self.assertTrue(sessione_delegato.is_text_present(etichetta.slug))
        self.assertEqual(sessione_delegato.url, '{}{}'.format(self.live_server_url, reverse('donazioni_etichetta', args=(etichetta.id,))))


class TestFunzionaliDonazioni(TestFunzionale):
    # Todo test date inizio e fine campagna non modificabili se sono presenti donazioni
    pass


class TestFunzionaliDonatori(TestFunzionale):

    def setUp(self):
        super(TestFunzionale, self).setUpClass()
        self.presidente = crea_persona()
        self.sede = crea_sede(self.presidente)
        self.campagna = crea_campagna(self.sede)

    def test_delegato_campagne_aggiunge_donazione(self):
        delegato = crea_persona()
        crea_utenza(delegato, email='delegato@cri.it')
        crea_appartenenza(delegato, self.sede)
        crea_delega(delegato, self.sede, DELEGATO_CAMPAGNE)
        sessione_delegato = self.sessione_utente(persona=delegato)
        sessione_delegato.visit("%s%s" % (self.live_server_url,
                                          self.campagna.url_aggiungi_donazione))
        dati_donazione = {'importo': '25',
                          'data': (self.campagna.inizio + timedelta(days=10)).strftime("%d/%m/%Y %H:%M"),
                          'nome': 'Mario',
                          'cognome': 'Rossi',
                          'email': 'mario.rossi@test.it'}
        sessione_delegato.select('metodo_pagamento', 'C')
        sessione_delegato.fill_form(dati_donazione)
        sessione_delegato.find_by_xpath("//button[@type='submit']").first.click()
        self.assertEqual(sessione_delegato.url, '{}{}'.format(self.live_server_url,
                                                              reverse('donazioni_campagne_donazioni', args=(self.campagna.id,))
                                                              )
                         )
        msg = 'Donazione aggiunta con successo: 25.00 € donati da Mario Rossi mario.rossi@test.it'
        self.assertTrue(sessione_delegato.is_text_present(msg))
        with sessione_delegato.get_iframe(0) as iframe:
            self.assertTrue(iframe.is_text_present('Mario Rossi mario.rossi@test.it'))

    def test_responsabile_campagna_aggiunge_donazione(self):
        responsabile = crea_persona()
        crea_utenza(responsabile, email='responsabile@cri.it')
        crea_appartenenza(responsabile, self.sede)
        crea_delega(responsabile, self.campagna, RESPONSABILE_CAMPAGNA)
        url_aggiungi_donazione = '{}{}'.format(self.live_server_url, self.campagna.url_aggiungi_donazione)
        sessione_responsabile = self.sessione_utente(persona=responsabile)
        sessione_responsabile.visit(url_aggiungi_donazione)
        dati_donazione = {'importo': '25',
                          'data': (self.campagna.inizio + timedelta(days=10)).strftime("%d/%m/%Y %H:%M"),
                          'nome': 'Mario',
                          'cognome': 'Rossi',
                          'email': 'mario.rossi@test.it'}
        sessione_responsabile.select('metodo_pagamento', 'C')
        sessione_responsabile.fill_form(dati_donazione)

        sessione_responsabile.find_by_xpath("//button[@type='submit']").first.click()
        self.assertEqual(sessione_responsabile.url, '{}{}'.format(self.live_server_url,
                                                                  reverse('donazioni_campagne_donazioni', args=(self.campagna.id,))
                                                                  )
                         )
        msg = 'Donazione aggiunta con successo: 25.00 € donati da Mario Rossi mario.rossi@test.it'
        self.assertTrue(sessione_responsabile.is_text_present(msg))
        with sessione_responsabile.get_iframe(0) as iframe:
            self.assertTrue(iframe.is_text_present('Mario Rossi mario.rossi@test.it'))
