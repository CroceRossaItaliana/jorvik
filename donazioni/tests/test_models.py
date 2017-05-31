from django.test import TestCase

from anagrafica.costanti import LOCALE, REGIONALE, TERRITORIALE
from anagrafica.permessi.applicazioni import DELEGATO_CAMPAGNE, RESPONSABILE_CAMPAGNA
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA
from base.utils_tests import crea_persona, crea_sede, crea_delega, crea_appartenenza, codice_fiscale
from donazioni.models import Etichetta
from donazioni.tests.utils import crea_campagna


class TestModelliCampagne(TestCase):

    @classmethod
    def setUpTestData(cls):
        presidente = crea_persona()
        persona = crea_persona()
        cls.sede = crea_sede(presidente)
        crea_appartenenza(persona, cls.sede)

    def test_responsabili_campagne(self):
        nome_campagna = 'Test Campagna'
        campagna = crea_campagna(self.sede, nome=nome_campagna)
        self.assertEqual(campagna.nome, nome_campagna)
        self.assertEqual(campagna.organizzatore, self.sede)
        persona = crea_persona()
        campagna.aggiungi_responsabile(persona)
        self.assertIn(persona, campagna.responsabili_attuali())

    def test_associa_etichette(self):
        nome_campagna = 'Test Campagna'
        campagna = crea_campagna(self.sede, nome=nome_campagna)
        etichetta = Etichetta(nome='Etichetta', comitato=self.sede)
        etichetta.save()
        campagna.etichette.add(etichetta)
        self.assertIn(campagna, etichetta.campagne.all())
        # Quando una campagna viene creata, viene creata e associata
        # un'etichetta con lo stesso nome della campagna (requisito B3)
        self.assertIn(campagna.nome, [s.nome for s in campagna.etichette.all()])
        self.assertIn(etichetta, campagna.etichette.all())

    def test_permessi_campagne(self):
        presidente = crea_persona()
        sicilia = crea_sede(presidente=presidente, estensione=REGIONALE)
        sicilia.codice_fiscale = codice_fiscale()
        sicilia.partita_iva = sicilia.codice_fiscale
        sicilia.save()
        catania = crea_sede(estensione=LOCALE, genitore=sicilia)
        maletto = crea_sede(estensione=TERRITORIALE, genitore=catania)

        delegato_campagne_catania = crea_persona()
        crea_delega(delegato_campagne_catania, sicilia, DELEGATO_CAMPAGNE)
        responsabile_campagna_terremoto_catania = crea_persona()
        campagna = crea_campagna(sicilia)
        campagna.aggiungi_delegato(RESPONSABILE_CAMPAGNA, responsabile_campagna_terremoto_catania)
        campagna2 = crea_campagna(maletto)

        # Il presidente ha tutti i permessi
        self.assertTrue(presidente.ha_permesso(GESTIONE_CAMPAGNE))
        self.assertTrue(presidente.ha_permesso(GESTIONE_CAMPAGNA))

        self.assertTrue(
            delegato_campagne_catania.oggetti_permesso(GESTIONE_CAMPAGNE).filter(pk=sicilia.pk),
            msg="Delegato non può gestire campagne per la sede"
        )

        self.assertTrue(
            delegato_campagne_catania.oggetti_permesso(GESTIONE_CAMPAGNA).filter(pk=campagna.pk),
            msg="Responsabile non può gestire la campagna in oggetto"
        )

        self.assertFalse(
            responsabile_campagna_terremoto_catania.oggetti_permesso(GESTIONE_CAMPAGNE).filter(pk=sicilia.pk),
            msg="Delegato non può gestire campagne per la sede"
        )

        self.assertTrue(
            responsabile_campagna_terremoto_catania.oggetti_permesso(GESTIONE_CAMPAGNA).filter(pk=campagna.pk),
            msg="Responsabile non può gestire la campagna in oggetto"
        )

        # il delegato campagne di una sede può gestire tutte le campagne delle sedi sottostanti
        self.assertTrue(
            delegato_campagne_catania.oggetti_permesso(GESTIONE_CAMPAGNE).filter(pk=maletto.pk),
            msg="Delegato non può gestire campagne per la sede"
        )

        self.assertFalse(
            responsabile_campagna_terremoto_catania.oggetti_permesso(GESTIONE_CAMPAGNA).filter(pk=campagna2.pk),
            msg="Responsabile non può gestire la campagna in oggetto"
        )

