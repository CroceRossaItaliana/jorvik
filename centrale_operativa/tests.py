from datetime import timedelta
from django.test import TestCase

from anagrafica.permessi.applicazioni import DELEGATO_CO
from anagrafica.permessi.costanti import GESTIONE_CENTRALE_OPERATIVA_SEDE
from attivita.models import Attivita
from django.utils import timezone

from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_area_attivita, crea_turno, \
    crea_partecipazione


class TestCentraleOperativa(TestCase):
    def test_poteri_temporanei(self):

        presidente = crea_persona()
        persona, sede, app = crea_persona_sede_appartenenza(presidente=presidente)

        ora = timezone.now()

        area, attivita = crea_area_attivita(sede)

        self.assertFalse(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona non ha di persé i permessi di gestione della CO"
        )

        self.assertTrue(
            presidente.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).first() == sede,
            "Il presidente ha i permessi di gestione della CO",
        )

        domani_inizio = ora + timedelta(hours=24)
        domani_fine = ora + timedelta(hours=25)

        t1 = crea_turno(attivita, inizio=domani_inizio, fine=domani_fine)
        partecipazione = crea_partecipazione(persona, t1)

        self.assertFalse(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona non ha ancora i permessi di gestione della CO"
        )

        attivita.centrale_operativa = Attivita.CO_AUTO
        attivita.save()

        self.assertFalse(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona non ha ancora i permessi di gestione della CO"
        )

        t1.inizio = ora
        t1.fine = ora + timedelta(hours=1)
        t1.save()

        self.assertTrue(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).first() == sede,
            "La persona può ora gestire la CO per la Sede"
        )

        self.assertTrue(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).count() == 1,
            "La persona può ora gestire la CO per la Sede solamente (non sotto unità)"
        )

        # Provo che il margine funzioni
        margine = Attivita.MINUTI_CENTRALE_OPERATIVA - 1

        t1.inizio = ora + timedelta(minutes=margine)
        t1.fine = ora + timedelta(minutes=2*margine)
        t1.save()

        self.assertTrue(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona può gestire la CO con un margine di %d minuti in anticipo" % margine,
        )

        t1.inizio = ora - timedelta(hours=24)
        t1.fine = ora - timedelta(minutes=margine)
        t1.save()

        self.assertTrue(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona può gestire la CO con un margine di %d minuti dopo la fine" % margine,
        )

        t1.inizio = ora - timedelta(hours=24)
        t1.fine = ora - timedelta(minutes=margine+2)
        t1.save()

        self.assertFalse(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona non puo gestire la CO se è troppo tardi",
        )

        # Se la partecipazione viene richiesta...
        partecipazione.richiedi()

        self.assertFalse(
            persona.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE).exists(),
            "La persona non può gestire la CO perché la richiesta non è stata processata"
        )


class TestFunzionaleCentraleOperativa(TestFunzionale):

    def test_centrale_operativa_permessi_attivita(self):

        delegato = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(DELEGATO_CO, delegato)

        area, attivita = crea_area_attivita(sede, centrale_operativa=None)
        turno = crea_turno(attivita)
        crea_partecipazione(volontario, turno)

        sessione_delegato = self.sessione_utente(persona=delegato)
        sessione_volontario = self.sessione_utente(persona=volontario)

        self.assertFalse(
            sessione_volontario.is_text_present("CO"),
            "La centrale operativa non e' disponibile al volontario"
        )

        self.assertTrue(
            sessione_delegato.is_text_present("CO"),
            "La centrale operativa e' disponibile al delegato"
        )

        # In modalita' automatica, il volontario e' abilitato immediatamente
        attivita.centrale_operativa = Attivita.CO_AUTO
        attivita.save()

        sessione_volontario.visit("%s/utente/" % self.live_server_url)

        self.assertTrue(
            sessione_volontario.is_text_present("CO"),
            "La centrale operativa e' ora disponibile al volontario"
        )

        sessione_volontario.click_link_by_partial_text("CO")
        sessione_volontario.click_link_by_partial_text("Turni")
        sessione_volontario.click_link_by_partial_text("Monta")

        self.assertTrue(
            sessione_volontario.is_text_present(attivita.nome),
            "Il volontario vede propria attivita in CO"
        )

        # In modalita' manuale...
        attivita.centrale_operativa = Attivita.CO_MANUALE
        attivita.save()

        sessione_volontario.click_link_by_partial_text("Smonta")

        self.assertTrue(
            sessione_volontario.is_text_present("Accesso Negato"),
            "Il volontario non può più montare o smontare"
        )

        sessione_delegato.click_link_by_partial_text("CO")
        sessione_delegato.click_link_by_partial_text("Poteri")

        self.assertTrue(
            sessione_delegato.is_text_present(volontario.nome),
            "Il delegato vede la persona in elenco"
        )

        sessione_delegato.click_link_by_partial_text("Assegna")

        self.assertTrue(
            sessione_delegato.is_text_present("Ritira"),
            "Il delegato ha correttamente abilitato i poteri"
        )

        sessione_volontario.click_link_by_partial_text("Torna")
        sessione_volontario.click_link_by_partial_text("CO")
        sessione_volontario.click_link_by_partial_text("Turni")
        sessione_volontario.click_link_by_partial_text("Smonta")

        self.assertTrue(
            sessione_volontario.is_text_present(volontario.nome),
            "Il volontario ha il suo nome in elenco"
        )
