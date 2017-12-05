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
    token = models.CharField(max_length=200, help_text='Token', blank=True)
    refresh_token = models.CharField(max_length=200, help_text='Refresh Token', blank=True)
    console_address = models.URLField(blank=True, help_text='Indirizzo della console MailUp. Es. https://a0f8a2.emailsp.com')

    @classmethod
    def sedi_con_account(cls):
        accounts = AccountMailUp.objects.prefetch_related('sede')
        return (a.sede for a in accounts)

    @cached_property
    def client(self):
        client = Client(str(self.client_id), str(self.client_secret),
                        self.username, self.password,
                        self.token, self.refresh_token)
        if not self.token:
            self.token, self.refresh_token = client.auth()
            self.save()
        return client

    def liste(self):
        client = self.client
        res, token_aggiornato = client.read_lists()
        if token_aggiornato:
            self._aggiorna_token()
        liste_res = [(l['IdList'], l.get('Name'),) for l in res.get('Items')]
        return liste_res

    def lista(self, id_lista):
        client = self.client
        res, token_aggiornato = client.read_list(id_lista)
        if token_aggiornato:
            self._aggiorna_token()
        return res

    def contatti(self, id_lista):
        client = self.client
        res, token_aggiornato = client.read_recipients(id_lista)
        if token_aggiornato:
            self._aggiorna_token()
        contatti_res = [{'email': r['Email']} for r in res.get('Items') if r.get('Status') == 'OPTIN']
        return contatti_res

    def crea_lista(self, body):

        client = self.client
        res, token_aggiornato = client.create_list(body)
        if token_aggiornato:
            self._aggiorna_token()
        return res['IdList']

    def _aggiorna_token(self):
        self.token = self.client.token
        self.refresh_token = self.client.refresh_token
        self.save()

    def iscrivi_email(self, id_lista, body):
        client = self.client
        res, token_aggiornato = client.subscribe(id_lista, body)
        if token_aggiornato:
            self._aggiorna_token()
        return res
