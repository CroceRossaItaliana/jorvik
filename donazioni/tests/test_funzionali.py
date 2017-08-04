from datetime import timedelta

from anagrafica.models import Appartenenza
from anagrafica.permessi.applicazioni import DELEGATO_CAMPAGNE, RESPONSABILE_CAMPAGNA
from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_sede, crea_persona, crea_delega, crea_appartenenza
from donazioni.tests.utils import crea_campagna


class TestFunzionaliCampagneEtichette(TestFunzionale):
    @classmethod
    def setUpClass(cls):
        super(TestFunzionale, cls).setUpClass()
        cls.presidente = crea_persona()
        cls.sede = crea_sede(cls.presidente)
        cls.delegato = crea_persona()
        cls.responsabile = crea_persona()
        crea_appartenenza(cls.delegato, cls.sede, Appartenenza.VOLONTARIO)
        crea_appartenenza(cls.responsabile, cls.sede, Appartenenza.VOLONTARIO)
        crea_delega(cls.delegato, cls.sede, DELEGATO_CAMPAGNE)

    def test_delegato_crea_campagna(self):
        pass


class TestFunzionaliDonatori(TestFunzionale):

    @classmethod
    def setUpClass(cls):
        super(TestFunzionale, cls).setUpClass()
        cls.presidente = crea_persona()
        cls.sede = crea_sede(cls.presidente)
        cls.campagna = crea_campagna(cls.sede)
        cls.delegato = crea_persona()
        cls.responsabile = crea_persona()
        crea_appartenenza(cls.delegato, cls.sede, Appartenenza.VOLONTARIO)
        crea_appartenenza(cls.responsabile, cls.sede, Appartenenza.VOLONTARIO)
        crea_delega(cls.delegato, cls.sede, DELEGATO_CAMPAGNE)
        crea_delega(cls.responsabile, cls.campagna, RESPONSABILE_CAMPAGNA)

    def test_delegato_aggiunge_donazione(self):
        sessione_delegato = self.sessione_utente(persona=self.delegato)
        sessione_delegato.visit("%s%s" % (self.live_server_url, self.campagna.url_aggiungi_donazione))
        dati_donazione = {'modalita': 'C',
                          'importo': '25.0',
                          'data': (self.campagna.inizio + timedelta(days=10)).strftime("%d/%m/%Y %H:%M"),
                          'nome': 'Mario',
                          'cognome': 'Rossi',
                          'email': 'mario.rossi@test.it'}
        sessione_delegato.fill_form(dati_donazione)
        sessione_delegato.find_by_xpath("//button[@type='submit']").first.click()
        msg = 'Donazione aggiunta con successo: 25.00 € donati da Mario Rossi mario.rossi@test.it '
        sessione_delegato.is_text_present(msg)
        with sessione_delegato.get_iframe(0) as iframe:
            self.assertFalse(iframe.is_text_present('Mario Rossi mario.rossi@test.it'))
