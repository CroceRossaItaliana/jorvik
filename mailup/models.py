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

    @classmethod
    def sedi_con_account(cls):
        accounts = AccountMailUp.objects.prefetch_related('sede')
        return [a.sede for a in accounts]

    @cached_property
    def client(self):
        return Client(self.client_id, self.client_secret, self.username, self.password)

