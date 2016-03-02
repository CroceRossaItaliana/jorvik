from datetime import timedelta
from django.test import TestCase

from anagrafica.permessi.costanti import GESTIONE_CENTRALE_OPERATIVA_SEDE
from attivita.models import Attivita
from django.utils import timezone
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

        attivita.centrale_operativa = True
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
