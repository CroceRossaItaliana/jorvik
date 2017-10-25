import requests

from .endpoints import ENDPOINTS


class MailUpException(Exception):
    pass


class MailUpAuthException(MailUpException):
    pass


class MailUpExpiredTokenException(MailUpAuthException):
    pass


class Client:
    def __init__(self, client_id, client_secret, username, password):
        self.id = client_id
        self.secret = client_secret
        self.username = username
        self.password = password
        self.token = ''
        self.refresh_token = ''
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
        if any(('ErrorCode' in response, 'ErrorName' in response)):
            error_code = response['ErrorCode']
            error_description = response['ErrorDescription']
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
        res = self._post(ENDPOINTS['token'], data)
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expiration_token_in = res['expires_in']

    def auth_refresh(self):
        data = {'grant_type': 'refresh_token',
                'client_id': self.id, 'client_secret': self.secret,
                'refresh_token': self.refresh_token, 'password': self.password}
        res = self._post(ENDPOINTS['token'], data)
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expiration_token_in = res['expires_in']

    def auth_headers(self):

        if self.token:
            return {'accept': 'application/json',
                    'authorization': 'Bearer {}'.format(self.token),
                    'content-type': 'application/json'}
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
        headers = {'accept': 'application/json',
                   'authorization': 'Bearer {}'.format(self.token),
                   'content-type': 'application/json'}
        res = self._get(ENDPOINTS['read_lists'], headers=headers)
        return res

    def _post(self, endpoint, data, **kwargs):
        try:
            res = requests.post(endpoint, data, **kwargs)
            self._check_errors(res)
        except ConnectionError as exc:
            res = {'ErrorCode': 500, 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': 'Endpoint non raggiungibile'}
            return res
        except MailUpExpiredTokenException:
            self.auth_refresh()
            res = self._post(endpoint, data, **kwargs)
        except MailUpException as exc:
            res = {'ErrorCode': exc.args[0], 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': exc.args[1]}
            return res
        return res.json()

    def _get(self, endpoint, **kwargs):
        try:
            res = requests.get(endpoint, **kwargs)
            self._check_errors(res)
        except ConnectionError as exc:
            res = {'ErrorCode': 500, 'ErrorName': exc.__class__.__name__,
                   'ErrorDescription': 'Endpoint non raggiungibile'}
        except MailUpExpiredTokenException:
            self.auth_refresh()
            res = self._get(endpoint, **kwargs)
        return res.json()
