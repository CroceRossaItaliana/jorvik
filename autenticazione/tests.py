from django.test import LiveServerTestCase

from base.utils_tests import crea_sessione, crea_persona, crea_utenza


class TestAutenticazione(LiveServerTestCase):

    def test_login(self):

        email = "una_prova@email.it"
        password = "una_password"

        persona = crea_persona()
        crea_utenza(persona, email=email, password=password)

        sessione = crea_sessione()
        sessione.visit("%s/login/" % self.live_server_url)
        sessione.fill("username", email)
        sessione.fill("password", password)
        sessione.find_by_css('button')[1].click()

        self.assertTrue(
            sessione.is_text_present(persona.nome)
        )