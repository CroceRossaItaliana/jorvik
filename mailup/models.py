from django.db import models
from django.utils.functional import cached_property

from base.models import ModelloSemplice

from .client import Client


class AccountMailUp(ModelloSemplice):
    sede = models.OneToOneField('anagrafica.Sede', related_name='account_mailup', on_delete=models.CASCADE)
    client_id = models.UUIDField(help_text='Client ID per il client MailUp')
    client_secret = models.UUIDField(help_text='Secret key per il client MailUp')
    username = models.CharField(max_length=100, help_text='Username di un account MailUp')
    password = models.CharField(max_length=100, help_text='Password di un account MailUp')
    token = models.CharField(max_length=200, help_text='Token')
    refresh_token = models.CharField(max_length=200, help_text='Refresh Token')

    @classmethod
    def sedi_con_account(cls):
        accounts = AccountMailUp.objects.prefetch_related('sede')
        return (a.sede for a in accounts)

    @cached_property
    def client(self):
        client = Client(self.client_id, self.client_secret,
                        self.username, self.password,
                        self.token, self.refresh_token)
        if not self.token:
            self.token, self.refresh_token = client.auth()
            self.save()
        return client

    def liste(self):
        client = self.client
        res = client.read_lists()
        liste_res = [(l['IdList'], l.get('Name'),) for l in res.get('Items')]
        return liste_res

    def contatti(self, id_lista):
        client = self.client
        res = client.read_recipients(id_lista)
        contatti_res = [{'email': r['Email']} for r in res.get('Items') if r.get('Status') == 'OPTIN']
        return contatti_res
