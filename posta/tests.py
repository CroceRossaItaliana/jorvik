import smtplib
from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

import freezegun
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.test import TestCase
from django.test import override_settings
from django.utils.timezone import now
from freezegun import freeze_time

from anagrafica.models import Persona
from base.utils_tests import crea_persona_sede_appartenenza, crea_utenza, email_fittizzia, crea_persona, crea_sede, \
    crea_appartenenza
from posta.models import Messaggio
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from posta.viste import posta_scrivi


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

    def test_flag_utenza_e_contatti_uguali(self):
        self.persona.email_contatto = self.persona.utenza.email
        self.persona.save()

        Messaggio.costruisci_e_invia(
            destinatari=[self.persona],
            oggetto="Stessa email",
            modello="email.html",
            utenza=True
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Stessa email') > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(self.persona.email_contatto, email.to)
        self.assertIn(self.persona.utenza.email, email.to)

        # Nessuna email di contatto
        self.persona.email_contatto = ''
        self.persona.save()

        Messaggio.costruisci_e_invia(
            destinatari=[self.persona],
            oggetto="Stessa email",
            modello="email.html",
            utenza=True
        )
        # c'è anche quella precedente
        self.assertEqual(len(mail.outbox), 2)
        email = mail.outbox[1]
        self.assertTrue(email.subject.find('Stessa email') > -1)
        self.assertEqual(len(email.to), 1)
        self.assertNotIn(self.persona.email_contatto, email.to)
        self.assertIn(self.persona.utenza.email, email.to)

    def test_flag_utenza_solo_email_di_contatto(self):
        self.persona.email_contatto = self.persona.utenza.email
        self.persona.save()
        self.persona.utenza = None
        self.persona.save()

        Messaggio.costruisci_e_invia(
            destinatari=[self.persona],
            oggetto="Email contatto",
            modello="email.html",
            utenza=True
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Email contatto') > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(self.persona.email_contatto, email.to)
        self.assertEqual(1, len(email.to))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class TestInviiMassivi(TestCase):

    num_persone = 100
    persone = []
    presidente = None
    sede = None

    def _invia_msg_singolo(self):
        Messaggio.costruisci_e_invia(
            destinatari=[self.persone[0].persona],
            oggetto="Email contatto",
            modello="email.html",
            utenza=True
        )

    def _reset_coda(self):
        Messaggio.objects.all().delete()

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.presidente = crea_persona()
        cls.presidente.email_contatto = email_fittizzia()
        crea_utenza(cls.presidente, email=cls.presidente.email_contatto)
        cls.sede = crea_sede(cls.presidente)
        for i in range(cls.num_persone):
            persona = crea_persona()
            crea_appartenenza(persona, cls.sede)
            persona.email_contatto = email_fittizzia()
            persona.save()
            cls.persone.append(crea_utenza(persona, email=email_fittizzia()))

    def _setup_request(self, path, utente, old_request=None):
        request = self.factory.get(path=path)
        if old_request:
            request.session = old_request.session
        else:
            engine = import_module(settings.SESSION_ENGINE)
            request.session = engine.SessionStore()
            request.session.save()
        request.user = utente
        return request

    def test_messaggio_elenco(self):
        request = self._setup_request('/', self.presidente.utenza)
        redirect = imposta_destinatari_e_scrivi_messaggio(request, Persona.objects.all())
        self.assertEqual(len(request.session["messaggio_destinatari"]), Persona.objects.all().count())
        request = self._setup_request(redirect['Location'], self.presidente.utenza, old_request=request)
        self.assertEqual(len(request.session["messaggio_destinatari"]), Persona.objects.all().count())
        response = posta_scrivi(request)
        # le persone generate dall'elenco sono presenti nel messaggio
        for persona in Persona.objects.all():
            self.assertContains(response, 'name="destinatari" type="hidden" value="{}"'.format(persona.pk))

        imposta_destinatari_e_scrivi_messaggio(request, Persona.objects.all())
        self.assertEqual(len(request.session["messaggio_destinatari"]), Persona.objects.all().count())
        request = self._setup_request(redirect['Location'], self.presidente.utenza, old_request=request)
        with freeze_time(now() + timedelta(seconds=settings.POSTA_MASSIVA_TIMEOUT + 1)):
            response = posta_scrivi(request)
            # le persone generate dall'elenco non sono presenti nel messaggio perché è scaduto il timeout
            for persona in Persona.objects.all():
                self.assertNotContains(response, 'name="destinatari" type="hidden" value="{}"'.format(persona.pk))

    def test_messaggio_senza_destinatari(self):
        messaggio = Messaggio.costruisci_e_accoda(
            destinatari=[],
            oggetto="Email contatto",
            modello="email.html",
        )
        messaggio._smaltisci_coda()
        self.assertEqual(Messaggio.in_coda().count(), 0)

    def test_messaggio_con_destinatario_vuoto(self):
        persona, sede, appartenenza = crea_persona_sede_appartenenza()
        persona.save()
        messaggio = Messaggio.costruisci_e_accoda(
            destinatari=[persona],
            oggetto="Email contatto",
            modello="email.html",
        )
        messaggio._smaltisci_coda()
        self.assertEqual(Messaggio.in_coda().count(), 0)

    @patch('smtplib.SMTP')
    def test_messaggio_senza_destinatari(self, mock_smtp):
        messaggio = Messaggio.costruisci_e_accoda(
            destinatari=[],
            oggetto="Email contatto",
            modello="email.html",
        )
        messaggio._smaltisci_coda()
        self.assertEqual(Messaggio.in_coda().count(), 0)

    @patch('smtplib.SMTP')
    def test_messaggio_con_destinatario_vuoto(self, mock_smtp):
        persona, sede, appartenenza = crea_persona_sede_appartenenza()
        persona.save()
        messaggio = Messaggio.costruisci_e_accoda(
            destinatari=[persona],
            oggetto="Email contatto",
            modello="email.html",
        )
        messaggio._smaltisci_coda()
        self.assertEqual(Messaggio.in_coda().count(), 0)

    @patch('smtplib.SMTP')
    def test_fallimento_autenticazione(self, mock_smtp):
        """
        In caso di fallimento autenticazione il messaggio viene rimesso in coda
        """
        self.assertEqual(Messaggio.in_coda().count(), 0)
        instance = mock_smtp.return_value
        instance.sendmail.side_effect = smtplib.SMTPAuthenticationError(code=530, msg='authentication error')

        self._invia_msg_singolo()
        self.assertEqual(Messaggio.in_coda().count(), 1)

    @patch('smtplib.SMTP')
    def test_fallimento_helo(self, mock_smtp):
        """
        In caso di fallimento durante helo il messaggio viene rimesso in coda, tranne che in caso
        di errore 5XX che è permanente
        """
        self.assertEqual(Messaggio.in_coda().count(), 0)
        codici = (500, 501, 504, 521, 421)
        for codice in codici:
            msg = 'code {}'.format(codice)
            instance = mock_smtp.return_value
            instance.sendmail.side_effect = smtplib.SMTPHeloError(code=codice, msg=msg)
            self._invia_msg_singolo()
            if codice == 501:
                self.assertEqual(Messaggio.in_coda().count(), 0)
            else:
                self.assertEqual(Messaggio.in_coda().count(), 1)
            self._reset_coda()

    @patch('smtplib.SMTP')
    def test_fallimento_connect(self, mock_smtp):
        """
        In caso di fallimento durante il connect il messaggio viene rimesso in coda
        """
        codici = (421,)
        for codice in codici:
            msg = 'code {}'.format(codice)
            instance = mock_smtp.return_value
            instance.sendmail.side_effect = smtplib.SMTPConnectError(code=codice, msg=msg)
            self._invia_msg_singolo()
            self.assertEqual(Messaggio.in_coda().count(), 1)
            self._reset_coda()

    @patch('smtplib.SMTP')
    def test_fallimento_data(self, mock_smtp):
        """
        In caso di fallimento durante il comando data  il messaggio viene rimesso in coda,
        tranne che in caso di errore 5XX che è permanente
        """
        codici = (451, 554, 500, 501, 503, 421, 552, 451, 452)
        for codice in codici:
            msg = 'code {}'.format(codice)
            instance = mock_smtp.return_value
            instance.sendmail.side_effect = smtplib.SMTPDataError(code=codice, msg=msg)
            self._invia_msg_singolo()
            if codice == 501:
                self.assertEqual(Messaggio.in_coda().count(), 0)
            else:
                self.assertEqual(Messaggio.in_coda().count(), 1)
            self._reset_coda()

    @patch('smtplib.SMTP')
    def test_fallimento_recipient(self, mock_smtp):
        """
        In caso di fallimento del recipient  il messaggio viene rimesso in coda se entrambi
        i recipient sono stati rifiutati, altrimenti viene considerato inviato
        """
        codici = (550, 551, 552, 553, 450, 451, 452, 500, 501, 503, 521, 421)
        for codice in codici:
            msg = 'code {}'.format(codice)
            instance = mock_smtp.return_value
            for x in range(2):
                recipients = {
                    self.persone[0].persona.email: (codice, msg) if x in (1, 2) else (250, 'ok'),
                    self.persone[0].email: (codice, msg) if x in (0, 2) else (250, 'ok'),
                }
                instance.sendmail.side_effect = smtplib.SMTPRecipientsRefused(recipients=recipients)
                self._invia_msg_singolo()
                if codice == 501 or x in (0, 1):
                    self.assertEqual(Messaggio.in_coda().count(), 0)
                else:
                    self.assertEqual(Messaggio.in_coda().count(), 1)
                self._reset_coda()

    @patch('smtplib.SMTP')
    def test_fallimento_sender(self, mock_smtp):
        """
        In caso di fallimento del sender il messaggio viene rimesso in coda,
        tranne che in caso di errore 5XX che è permanente
        """
        codici = (451, 452, 500, 501, 421)
        for codice in codici:
            msg = 'code {}'.format(codice)
            instance = mock_smtp.return_value
            instance.sendmail.side_effect = smtplib.SMTPSenderRefused(code=codice, msg=msg, sender=Messaggio.SUPPORTO_EMAIL)
            self._invia_msg_singolo()
            if codice == 501:
                self.assertEqual(Messaggio.in_coda().count(), 0)
            else:
                self.assertEqual(Messaggio.in_coda().count(), 1)
            self._reset_coda()

    @patch('smtplib.SMTP')
    def test_fallimento_disconnect(self, mock_smtp):
        """
        In caso di disconessione del server il messaggio viene rimesso in coda
        """
        instance = mock_smtp.return_value
        instance.sendmail.side_effect = smtplib.SMTPServerDisconnected({})
        self._invia_msg_singolo()
        self.assertEqual(Messaggio.in_coda().count(), 1)
        self._reset_coda()
