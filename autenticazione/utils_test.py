from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase

from base.utils_tests import sessione_utente


class TestFunzionale(StaticLiveServerTestCase):

    sessioni_aperte = []

    def __init__(self, *args, **kwargs):
        self.__class__.sessioni_aperte = []
        super(TestFunzionale, self).__init__(*args, **kwargs)

    def sessione_utente(self, **kwargs):
        sessione = sessione_utente(self.live_server_url, **kwargs)
        self.sessioni_aperte.append(sessione)
        return sessione

    def seleziona_delegati(self, sessione, persone):
        with sessione.get_iframe(0) as iframe:
            import time

            for persona in persone:
                iframe.type('persona-autocomplete', persona.nome)
                time.sleep(1.5)
                iframe.find_by_xpath("//span[@data-value='%d']" % persona.pk).first.click()
                iframe.find_by_xpath("//button[@type='submit']").first.click()

            iframe.click_link_by_partial_text('Continua')

    def presente_in_elenco(self, sessione, persona):
        # Genera con impostazioni di default (clicca due volte su "Genera")
        sessione.find_by_xpath("//button[@type='submit']").first.click()
        with sessione.get_iframe(0) as iframe:  # Dentro la finestra
            if iframe.is_text_present("Genera elenco"):
                iframe.find_by_xpath("//button[@type='submit']").first.click()
            # Cerca la persona
            iframe.fill('filtra', persona.codice_fiscale)
            iframe.find_by_xpath("//button[@type='submit']").first.click()
            return iframe.is_text_present(persona.nome)

    def seleziona_delegato(self, sessione, persona):
        self.seleziona_delegati(sessione, [persona])

    def scrivi_tinymce(self, sessione, nome, testo):
        with sessione.get_iframe("id_%s_ifr" % nome) as iframe:
            iframe.find_by_tag('body').type(testo)

    def tearDown(self):
        if not hasattr(self, 'mantieni_aperto'):
            sessioni_aperte = list(self.sessioni_aperte)
            for sessione in sessioni_aperte:
                self.sessioni_aperte.remove(sessione)
                #sessione.quit()
        super(TestFunzionale, self).tearDown()
