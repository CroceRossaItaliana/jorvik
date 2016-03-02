from django.test import LiveServerTestCase

from base.utils_tests import sessione_utente


class TestFunzionale(LiveServerTestCase):

    def __init__(self, *args, **kwargs):
        self.sessioni_aperte = []
        super(TestFunzionale, self).__init__(*args, **kwargs)

    def sessione_utente(self, **kwargs):
        sessione = sessione_utente(self.live_server_url, **kwargs)
        self.sessioni_aperte.append(sessione)
        return sessione

    def tearDown(self):
        for sessione in self.sessioni_aperte:
            sessione.quit()
        super(TestFunzionale, self).tearDown()
