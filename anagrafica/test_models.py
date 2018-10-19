from django import test

from base.utils import poco_fa, mezzanotte_24
from base.utils_tests import crea_delega


class DelegaModelTest(test.TestCase):
    def test_termina_method_fine_is_poco_fa(self):
        now = poco_fa()
        delega = crea_delega()
        delega.termina(termina_at=now)
        self.assertEqual(delega.fine, now)
    
    def test_termina_method_fine_is_mezzanotte_24(self):
        delega = crea_delega()
        delega.termina()
        self.assertEqual(delega.fine, mezzanotte_24())