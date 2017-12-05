import json

import requests

from .endpoints import ENDPOINTS


class MailUpException(Exception):
    pass


class MailUpAuthException(MailUpException):
    pass


class MailUpExpiredTokenException(MailUpAuthException):
    pass


class Client:
    def __init__(self, client_id, client_secret, username, password, token='', refresh_token=''):
        self.id = client_id
        self.secret = client_secret
        self.username = username
        self.password = password
        self.token = token
        self.refresh_token = refresh_token
        self.expiration_token_in = 0

    @classmethod
    def _check_errors(cls, response):
        """
        Error response sample
        {'ErrorCode': '400',
         'ErrorDescription': 'The given key was not present in the dictionary.',
         'ErrorName': 'BadRequest',
         'ErrorStack': None}
        """
        try:
            res = response.json()
        except ValueError:
            error_code = '500'
            error_description = 'MailUp REST API server error'
            raise MailUpException(error_code, error_description)
        else:
            if isinstance(res, dict) and any(('ErrorCode' in res, 'ErrorName' in res)):
                error_code = res['ErrorCode']
                error_description = res['ErrorDescription']
                if error_code == '401' and 'expired' in error_description:
                    raise MailUpExpiredTokenException('Token scaduto. Eseguire client.auth_refresh()')
                raise MailUpException(error_code, error_description)

    def auth(self):
        """
        Response:
        {   "access_token":"MYACCESSTOKEN",
            "expires_in":900,
            "refresh_token":"MYREFRESHTOKEN"}
        """
        data = {'grant_type': 'password',
                'client_id': self.id, 'client_secret': self.secret,
                'username': self.username, 'password': self.password}
        res, _ = self._post(ENDPOINTS['token'], data)
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expiration_token_in = res['expires_in']
        return self.token, self.refresh_token

    def auth_refresh(self):
        data = {'grant_type': 'refresh_token',
                'client_id': self.id, 'client_secret': self.secret,
                'refresh_token': self.refresh_token, 'password': self.password}
        res, _ = self._post(ENDPOINTS['token'], data)
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expiration_token_in = res['expires_in']
        return res

    @property
    def auth_headers(self):
        if self.token:
            return {'Accept': 'application/json',
                    'Authorization': 'Bearer {}'.format(self.token),
                    'Content-type': 'application/json'}
        else:
            raise MailUpAuthException('Client non autenticato. Eseguire prima client.auth()')

    def read_lists(self):
        """
        return:
        {'IsPaginated': False,
         'Items': [{'Company': '',
           'Description': 'Iscritti alla newsletter.',
           'IdList': 1,
           'ListGuid': 'aafa5375-bcf1-4e06-965a-e3a98b626156',
           'Name': 'Newsletter'}],
         'PageNumber': 0,
         'PageSize': 20,
         'Skipped': 0,
         'TotalElementsCount': 1}
        """
        if not self.token:
            self.auth()
        res, refreshed = self._get(ENDPOINTS['read_lists'], headers=self.auth_headers)
        return res, refreshed

    def read_list(self, id_list):
        if not self.token:
            self.auth()
        res, refreshed = self._get(ENDPOINTS['get_list'].format(id_list), headers=self.auth_headers)
        return res, refreshed

    def create_list(self, body):
        body = json.dumps(body)
        if not self.token:
            self.auth()
        endpoint = ENDPOINTS['create_list']
        res, refreshed = self._post(endpoint, body, headers=self.auth_headers)
        return res, refreshed

    def read_recipients(self, id_list):
        if not self.token:
            self.auth()
        endpoint = ENDPOINTS['read_recipients'].format(id_list) + '?PageSize=1000'
        res, refreshed = self._get(endpoint, headers=self.auth_headers)
        return res, refreshed

    def subscribe(self, id_list, body):
        body = json.dumps(body)
        if not self.token:
            self.auth()
        endpoint = ENDPOINTS['subscribe'].format(id_list)
        res, refreshed = self._post(endpoint, body, headers=self.auth_headers)
        return res, refreshed

    def _post(self, endpoint, data, **kwargs):

        try:
            res = requests.post(endpoint, data=data, **kwargs)
            self._check_errors(res)
        except ConnectionError as exc:
            res = {'ErrorCode': 500, 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': 'Endpoint non raggiungibile'}
            return res, False
        except MailUpExpiredTokenException:
            self.auth_refresh()
            kwargs['headers'] = self.auth_headers
            res = requests.post(endpoint, data, **kwargs)
            return res.json(), True
        except MailUpException as exc:
            res = {'ErrorCode': exc.args[0], 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': exc.args[1]}
            return res, False
        else:
            return res.json(), False

    def _get(self, endpoint, **kwargs):
        try:
            res = requests.get(endpoint, **kwargs)
            self._check_errors(res)
        except ConnectionError as exc:
            res = {'ErrorCode': 500, 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': 'Endpoint non raggiungibile'}
            return res, False
        except MailUpExpiredTokenException:
            self.auth_refresh()
            kwargs['headers'] = self.auth_headers
            res = requests.get(endpoint, **kwargs)
            return res.json(), True
        except MailUpException as exc:
            res = {'ErrorCode': exc.args[0], 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': exc.args[1]}
            return res, False
        else:
            return res.json(), False
