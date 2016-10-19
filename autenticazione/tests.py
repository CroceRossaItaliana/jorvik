from django.utils.timezone import now
from freezegun import freeze_time

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

        with freeze_time("2016-01-20 10:34:50"):
            self.assertIsNone(utente.ultima_azione)
            response = self.client.post(settings.LOGIN_URL, data={
                'auth-username': utente.email, 'auth-password': 'prova',
                'jorvik_login_view-current_step': 'auth'
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('two_factor:profile'))

            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, now())

        with freeze_time("2016-01-20 10:56:50"):
            response = self.client.post(settings.LOGOUT_URL)
            self.assertContains(response, 'Sei uscito da Gaia')
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, now())

        with freeze_time("2016-01-20 11:16:50"):
            StaticDevice.objects.create(user=utente, name="Device")
            response = self.client.post(settings.LOGIN_URL, data={
                'auth-username': utente.email, 'auth-password': 'prova',
                'jorvik_login_view-current_step': 'auth'
            })
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/utente/', fetch_redirect_response=False)
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, now())

        with freeze_time("2016-01-20 11:26:50"):
            response = self.client.get('/utente/')
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, now())

        with freeze_time("2016-01-20 11:28:50"):
            response = self.client.get(reverse('two_factor:profile'))
            utente = self._ricarica_model(utente._meta.model, utente)
            self.assertEqual(utente.ultima_azione, now())
