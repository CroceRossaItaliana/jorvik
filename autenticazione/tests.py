from unittest.mock import Mock, patch
import datetime

from django.utils.timezone import now

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_otp.plugins.otp_static.models import StaticDevice

from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_persona, crea_utenza


class TestAutenticazione(TestFunzionale):
    def test_login(self):
        persona = crea_persona()
        sessione = self.sessione_utente(persona=persona)

        self.assertTrue(
            True,
            "Login effettuato con successo",
        )

    def test_logout(self):
        persona = crea_persona()
        sessione = self.sessione_utente(persona=persona)

        sessione.visit("%s/logout/" % self.live_server_url)

        self.assertFalse(
            sessione.is_text_present(persona.nome),
            "Logout effettuato con successo"
        )


class TestMiddleware2FA(TestCase):
    def _ricarica_model(self, model, obj):
        return model.objects.get(pk=obj.pk)

    def test_aggiornamento_ultima_azione(self):
        persona = crea_persona()
        utente = crea_utenza(persona)
        utente.is_staff = True
        utente.richiedi_2fa = True
        utente.save()

        data_base = datetime.datetime(2016, 1, 11, 12, 34, 56)
        data_1 = data_base + datetime.timedelta(seconds=60)
        data_2 = data_base + datetime.timedelta(seconds=120)
        data_3 = data_base + datetime.timedelta(seconds=180)
        data_4 = data_base + datetime.timedelta(seconds=240)
        data_5 = data_base + datetime.timedelta(seconds=130*60)

        mock_time = Mock()
        mock_time.return_value = data_base
        # simulazione del login e richiesta di attivazione 2FA
        # la data dell'ultima azione viene aggiornata
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            self.assertIsNone(utente.ultima_azione)
            response = self.client.post(settings.LOGIN_URL, data={
                'auth-username': utente.email, 'auth-password': 'prova',
                'jorvik_login_view-current_step': 'auth'
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('two_factor:profile'))

            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_base)

        # simulazione del logout
        # la data dell'ultima azione non viene aggiornata
        mock_time.return_value = data_1
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            response = self.client.post(settings.LOGOUT_URL)
            self.assertContains(response, 'Sei uscito da Gaia')
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_base)

        # Login con device 2FA attivo
        # L'utente viene accettato e diretto alla home
        # la data dell'ultima azione viene aggiornata
        mock_time.return_value = data_2
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            StaticDevice.objects.create(user=utente, name="Device")
            response = self.client.post(settings.LOGIN_URL, data={
                'auth-username': utente.email, 'auth-password': 'prova',
                'jorvik_login_view-current_step': 'auth'
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/utente/', fetch_redirect_response=False)
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_2)

        # visita di una pagina normale del sito
        # la data dell'ultima azione viene aggiornata
        mock_time.return_value = data_3
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            response = self.client.get('/utente/')
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_3)

        # visita di una pagina di servizio
        # la data dell'ultima azione non viene aggiornata
        mock_time.return_value = data_4
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            response = self.client.get(reverse('two_factor:profile'))
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_3)

        # visita di una pagina di servizio
        # la data dell'ultima azione non viene aggiornata
        mock_time.return_value = data_5
        with patch('autenticazione.two_factor.middleware.now', return_value=mock_time()):
            response = self.client.get(settings.TWO_FACTOR_SESSIONE_SCADUTA)
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, data_3)
