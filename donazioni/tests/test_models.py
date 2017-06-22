from datetime import datetime
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from anagrafica.costanti import LOCALE, REGIONALE, TERRITORIALE
from anagrafica.permessi.applicazioni import DELEGATO_CAMPAGNE, RESPONSABILE_CAMPAGNA
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA, COMPLETO
from base.utils import poco_fa
from base.utils_tests import crea_persona, crea_sede, crea_delega, crea_appartenenza, codice_fiscale
from donazioni.models import Etichetta, Campagna, Donazione, Donatore
from donazioni.tests.utils import crea_campagna, aggiungi_responsabile_campagna, mock_autonow


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
        aggiungi_responsabile_campagna(campagna, persona)
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

    def test_elimina_etichetta_con_campagne_associate_unica_etichetta(self):
        nome_campagna = 'Test Campagna'
        campagna = crea_campagna(self.sede, nome=nome_campagna)
        campagna_id = campagna.id
        etichetta = Etichetta(nome='Etichetta', comitato=self.sede)
        etichetta.save()
        campagna.etichette.add(etichetta)
        self.assertEqual(campagna.etichette.count(), 2)
        etichetta.delete()
        self.assertEqual(campagna.etichette.count(), 1)
        etichetta_default = campagna.etichette.all()[0]
        # elimino anche l'etichetta di default
        etichetta_default.delete()
        campagna = Campagna.objects.get(pk=campagna_id)
        # campagna resta senza etichette
        self.assertEqual(campagna.nome, nome_campagna)
        self.assertEqual(campagna.etichette.count(), 0)

    def test_permessi_campagne(self):
        presidente = crea_persona()
        sicilia = crea_sede(presidente=presidente, estensione=REGIONALE)
        sicilia.codice_fiscale = codice_fiscale()
        sicilia.partita_iva = sicilia.codice_fiscale
        sicilia.save()
        catania = crea_sede(estensione=LOCALE, genitore=sicilia)
        maletto = crea_sede(estensione=TERRITORIALE, genitore=catania)

        delegato_campagne_sicilia = crea_persona()
        crea_delega(delegato_campagne_sicilia, sicilia, DELEGATO_CAMPAGNE)
        responsabile_campagna_terremoto_catania = crea_persona()
        campagna = crea_campagna(sicilia)
        campagna.aggiungi_delegato(RESPONSABILE_CAMPAGNA, responsabile_campagna_terremoto_catania)
        campagna2 = crea_campagna(maletto)

        # Il presidente ha tutti i permessi
        self.assertTrue(presidente.ha_permesso(GESTIONE_CAMPAGNE))
        self.assertTrue(presidente.ha_permesso(GESTIONE_CAMPAGNA))

        self.assertTrue(
            delegato_campagne_sicilia.oggetti_permesso(GESTIONE_CAMPAGNE).filter(pk=sicilia.pk),
            msg="Delegato non può gestire campagne per la sede"
        )

        self.assertTrue(
            delegato_campagne_sicilia.oggetti_permesso(GESTIONE_CAMPAGNA).filter(pk=campagna.pk),
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

        # il delegato campagne di una sede può gestire tutte le campagne delle sedi sottostanti (ma non le territoriali)
        self.assertFalse(
            delegato_campagne_sicilia.oggetti_permesso(GESTIONE_CAMPAGNE).filter(pk=maletto.pk),
            msg="Delegato non può gestire campagne per la sede"
        )

        self.assertFalse(
            responsabile_campagna_terremoto_catania.oggetti_permesso(GESTIONE_CAMPAGNA).filter(pk=campagna2.pk),
            msg="Responsabile non può gestire la campagna in oggetto"
        )

        # check permessi etichette
        etichetta_sicilia = Etichetta.objects.create(nome='test', comitato=sicilia)
        self.assertTrue(delegato_campagne_sicilia.permessi_almeno(etichetta_sicilia, COMPLETO))
        self.assertFalse(responsabile_campagna_terremoto_catania.permessi_almeno(etichetta_sicilia, COMPLETO))


class TestModelliDonazioniDonatori(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.sede = crea_sede(crea_persona())
        cls.campagna = crea_campagna(cls.sede)

    def test_crea_donazione(self):
        donazione = Donazione.objects.create(campagna=self.campagna, importo=100, data=poco_fa())
        self.assertEqual(donazione.campagna, self.campagna)

    def test_donazione_negativa(self):
        with self.assertRaises(ValidationError):
            donazione = Donazione.objects.create(campagna=self.campagna, importo=-100, data=poco_fa())
            donazione.full_clean()

    def test_crea_donazioni_senza_data(self):
        """
        Test per il requisito C-4
        Per ogni donazione sarà possibile inserire la data della donazione. Ove non
        specificata, questa sarà impostata alla data corrente se la donazione prece-
        dente in ordine temporale è stata fatta in giorni precedenti. Se la donazione
        precedente è stata inserita in data odierna, viene usata la “data donazione” di
        quest’ultima.
        """
        # mock di timezone.now per il default del campo 'creazione' per simulare una donazione
        # inserita in giorni precedenti
        field = Donazione._meta.get_field('creazione')
        with mock.patch.object(field, 'default', new=mock_autonow):
            donazione_1 = Donazione.objects.create(campagna=self.campagna, importo=100)
        donazione_2 = Donazione.objects.create(campagna=self.campagna, importo=100)
        # donazione_2 inserita un giorno successivo alla donazione_1 ==> le date saranno poco_fa() per entrambi
        self.assertNotEqual(donazione_1.data, donazione_2.data)

        donazione_3 = Donazione.objects.create(campagna=self.campagna, importo=100)
        # donazione_3 inserita lo stesso giorno di donazione_2 ==> avranno stessa data
        self.assertEqual(donazione_2.data, donazione_3.data)

    def test_riconcilia_donatori(self):
        Donatore.objects.create(email='test@test.com')
        donatore_2 = Donatore(nome='Fabio', cognome='Nappo', email='test@test.com')
        istanza = Donatore.nuovo_o_esistente(donatore_2)
        self.assertEqual(istanza.email, donatore_2.email)
        self.assertEqual(istanza.nome, donatore_2.nome)
        self.assertEqual(istanza.cognome, donatore_2.cognome)

        Donatore.objects.create(codice_fiscale='nppdnc78b03e791v')
        donatore_2 = Donatore(nome='Domenico', cognome='Nappo', codice_fiscale='nppdnc78b03e791v')
        istanza = Donatore.nuovo_o_esistente(donatore_2)
        self.assertEqual(istanza.email, '')
        self.assertEqual(istanza.nome, donatore_2.nome)
        self.assertEqual(istanza.cognome, donatore_2.cognome)
        self.assertEqual(istanza.codice_fiscale, donatore_2.codice_fiscale)
        id_donatore_con_cf = istanza.id

        data_nascita = poco_fa()
        Donatore.objects.create(nome='Domenico', cognome='Nappo', data_nascita=data_nascita, comune_nascita='Test')
        donatore_2 = Donatore(nome='Domenico', cognome='Nappo', data_nascita=data_nascita, comune_nascita='Test',
                              email='test2@test.com')
        istanza = Donatore.nuovo_o_esistente(donatore_2)
        self.assertEqual(istanza.email, donatore_2.email)
        self.assertEqual(istanza.data_nascita, donatore_2.data_nascita)
        self.assertEqual(istanza.comune_nascita, donatore_2.comune_nascita)
        self.assertEqual(istanza.codice_fiscale, '')

        donatore_2 = Donatore(email='test3@test.it', codice_fiscale='nppdnc78b03e791v')
        istanza = Donatore.nuovo_o_esistente(donatore_2)
        self.assertEqual(istanza.id, id_donatore_con_cf)
        self.assertEqual(istanza.email, 'test3@test.it')
        self.assertEqual(istanza.codice_fiscale, 'nppdnc78b03e791v')
        # self.assertEqual(istanza.nome, 'Domenico')
        # self.assertEqual(istanza.cognome, 'Nappo')
