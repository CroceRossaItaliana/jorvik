from django.test import TestCase
from django.db.models.fields import related_descriptors
from base.utils_tests import crea_persona, crea_sede, crea_delega, crea_appartenenza, codice_fiscale
from mailup.models import AccountMailUp


class TestAccountMailUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sede_1 = crea_sede(crea_persona())
        cls.sede_2 = crea_sede(crea_persona())

    def test_crea_account(self):
        AccountMailUp.objects.create(sede=self.sede_1,
                                     client_id='ef8a70f1-6d35-4d48-83a2-06f8d153e66e',
                                     client_secret='2e9e0157-7bfb-4efa-aba8-f216617fe5fa',
                                     username='test', password='test')
        self.assertIsNotNone(self.sede_1.account_mailup)
        with self.assertRaises(AccountMailUp.DoesNotExist):
            account = self.sede_2.account_mailup
        self.assertIsNone(self.sede_2.mailup)
        self.assertEqual(self.sede_1.account_mailup.sede, self.sede_1)
        self.assertEqual(self.sede_1.account_mailup.username, 'test')

    def test_sedi_con_account(self):
        AccountMailUp.objects.create(sede=self.sede_1,
                                     client_id='ef8a70f1-6d35-4d48-83a2-06f8d153e66e',
                                     client_secret='2e9e0157-7bfb-4efa-aba8-f216617fe5fa',
                                     username='test', password='test')
        AccountMailUp.objects.create(sede=self.sede_2,
                                     client_id='ef8a70f1-6d35-4d48-83a2-06f8d153e66e',
                                     client_secret='2e9e0157-7bfb-4efa-aba8-f216617fe5fa',
                                     username='test', password='test')
        sedi = AccountMailUp.sedi_con_account()
        self.assertListEqual(sedi, [self.sede_1, self.sede_2])
