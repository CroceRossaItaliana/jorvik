
from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_sessione, crea_persona, crea_utenza, sessione_utente


class TestAutenticazione(TestFunzionale):

    def test_login(self):

        email = "una_prova@email.it"
        password = "una_password"

        persona = crea_persona()
        crea_utenza(persona, email=email, password=password)

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

