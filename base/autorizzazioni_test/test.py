import datetime

from django.test import TestCase
from lxml import html

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, TERRITORIALE
from anagrafica.forms import ModuloCreazioneEstensione, ModuloNegaEstensione, ModuloProfiloModificaAnagrafica
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Delega
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, PRESIDENTE, UFFICIO_SOCI_UNITA
from anagrafica.permessi.costanti import MODIFICA, ELENCHI_SOCI, LETTURA, GESTIONE_SOCI
from autenticazione.models import Utenza
from autenticazione.utils_test import TestFunzionale
from base.models import Autorizzazione
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, email_fittizzia, \
    crea_utenza
from posta.models import Messaggio

from base.autorizzazioni_test.models import ApprovaAutorizzazioneTest, NegaAutorizzazioneTest


class TestAutorizzazioni(TestCase):

    def test_autorizzazione_accettata(self):
        presidente = crea_persona()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        persona = crea_persona()
        appartenenza = crea_appartenenza(persona, sede)

        delega_presidente = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=50),
            fine=datetime.datetime.now() + datetime.timedelta(days=50)
        )
        delega_presidente.save()

        self.assertFalse(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        da_approvare = ApprovaAutorizzazioneTest.objects.create(
            richiedente=persona,
            persona=persona,
            destinazione=sede,
            appartenenza=appartenenza,
            motivo='Un motivo qualsiasi'
        )

        da_approvare.creazione = datetime.datetime.now() - datetime.timedelta(days=60)
        da_approvare.save()
        da_approvare.richiedi()

        self.assertFalse(da_approvare.automatica)

        self.assertTrue(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        aut = presidente.autorizzazioni_in_attesa().first()

        self.assertTrue(aut)

        da_approvare.controlla_concedi_automatico()

        self.assertTrue(da_approvare.automatica)

        aut = presidente.autorizzazioni_in_attesa().first()
        self.assertFalse(aut)

        self.assertFalse(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni da processare"
        )

        self.assertIn(da_approvare, ApprovaAutorizzazioneTest.con_esito_ok())

    def test_autorizzazione_accettata_fail(self):
        presidente = crea_persona()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        persona = crea_persona()
        appartenenza = crea_appartenenza(persona, sede)

        delega_presidente = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=50),
            fine=datetime.datetime.now() + datetime.timedelta(days=50)
        )
        delega_presidente.save()

        self.assertFalse(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        da_approvare = ApprovaAutorizzazioneTest.objects.create(
            richiedente=persona,
            persona=persona,
            destinazione=sede,
            appartenenza=appartenenza,
            motivo='Un motivo qualsiasi'
        )

        da_approvare.richiedi()

        self.assertFalse(da_approvare.automatica)

        self.assertTrue(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        aut = presidente.autorizzazioni_in_attesa().first()

        self.assertTrue(aut)

        da_approvare.controlla_concedi_automatico()

        self.assertFalse(da_approvare.automatica)

        aut = presidente.autorizzazioni_in_attesa().first()
        self.assertTrue(aut)

        self.assertTrue(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        self.assertNotIn(da_approvare, ApprovaAutorizzazioneTest.con_esito_ok())


    def test_autorizzazione_negata(self):
        presidente = crea_persona()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        persona = crea_persona()
        appartenenza = crea_appartenenza(persona, sede)

        delega_presidente = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=50),
            fine=datetime.datetime.now() + datetime.timedelta(days=50)
        )
        delega_presidente.save()

        self.assertFalse(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        da_approvare = NegaAutorizzazioneTest.objects.create(
            richiedente=persona,
            persona=persona,
            destinazione=sede,
            appartenenza=appartenenza,
            motivo='Un motivo qualsiasi'
        )

        da_approvare.creazione = datetime.datetime.now() - datetime.timedelta(days=60)
        da_approvare.save()
        da_approvare.richiedi()

        self.assertFalse(da_approvare.automatica)

        self.assertTrue(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        aut = presidente.autorizzazioni_in_attesa().first()

        self.assertTrue(aut)

        da_approvare.controlla_nega_automatico()

        self.assertTrue(da_approvare.automatica)

        aut = presidente.autorizzazioni_in_attesa().first()
        self.assertFalse(aut)

        self.assertIn(da_approvare, NegaAutorizzazioneTest.con_esito_no())

    def test_autorizzazione_negata_fail(self):
        presidente = crea_persona()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        persona = crea_persona()
        appartenenza = crea_appartenenza(persona, sede)

        delega_presidente = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=50),
            fine=datetime.datetime.now() + datetime.timedelta(days=50)
        )
        delega_presidente.save()

        self.assertFalse(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        da_approvare = NegaAutorizzazioneTest.objects.create(
            richiedente=persona,
            persona=persona,
            destinazione=sede,
            appartenenza=appartenenza,
            motivo='Un motivo qualsiasi'
        )

        da_approvare.richiedi()

        self.assertFalse(da_approvare.automatica)

        self.assertTrue(
            presidente.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        aut = presidente.autorizzazioni_in_attesa().first()

        self.assertTrue(aut)

        da_approvare.controlla_nega_automatico()

        self.assertFalse(da_approvare.automatica)

        aut = presidente.autorizzazioni_in_attesa().first()
        self.assertTrue(aut)

        self.assertNotIn(da_approvare, NegaAutorizzazioneTest.con_esito_no())
