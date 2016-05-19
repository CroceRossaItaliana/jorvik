from django.core import mail
from django.test import TestCase

from base.utils_tests import crea_persona_sede_appartenenza, crea_sede, crea_utenza, email_fittizzia
from posta.models import Messaggio


class TestMessaggio(TestCase):

    def setUp(self):
        persona, sede, appartenenza = crea_persona_sede_appartenenza()
        self.persona = persona
        self.persona.email_contatto = email_fittizzia()
        self.persona.save()
        self.utenza = crea_utenza(persona=self.persona, email=email_fittizzia())

    def test_flag_no_utenza(self):

        Messaggio.costruisci_e_invia(
            destinatari=[self.persona],
            oggetto="Solo email di contatto",
            modello="email.html"
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Solo email di contatto') > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(self.persona.email_contatto, email.to)
        self.assertNotIn(self.persona.utenza.email, email.to)

    def test_flag_utenza(self):
        Messaggio.costruisci_e_invia(
            destinatari=[self.persona],
            oggetto="Entrambe le email",
            modello="email.html",
            utenza=True
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Entrambe le email') > -1)
        self.assertEqual(len(email.to), 2)
        self.assertIn(self.persona.email_contatto, email.to)
        self.assertIn(self.persona.utenza.email, email.to)
