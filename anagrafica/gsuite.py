from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from jorvik.settings import GSUITE_CONF


class GsuiteLib:

    def __init__(self, gsettings):
        self.account_email = gsettings.get('service', 'account_email')
        self.account_pkcs12_file_path = gsettings.get('service', 'account_pkcs12_file_path')
        self.secret = gsettings.get('service', 'secret') or 'notasecret'
        self.scopes = gsettings.get('service', 'scopes').split(',')
        self.bind_user = gsettings.get('service', 'bind_user')
        self.base_domain = gsettings.get('service', 'base_domain')
        self.service = None

    def init_service(self, service):
        if service == 'directory_v1':
            self.service = self.create_directory_service(self.bind_user)
            return

        raise NotImplementedError("Only directory_v1 implemented")

    def create_directory_service(self, user_email):

        credentials = ServiceAccountCredentials.from_p12_keyfile(
            self.account_email,
            self.account_pkcs12_file_path,
            self.secret,
            scopes=self.scopes)

        credentials = credentials.create_delegated(user_email)

        return build('admin', 'directory_v1', credentials=credentials)

    def list_users(self, customer='my_customer', limit=10, order_by='email'):
        results = self.service.users().list(customer=customer, maxResults=limit,
                                            orderBy=order_by).execute()
        return results.get('users', [])

    def new_user(self, data, genera_password=False):
        from anagrafica.utils import random_password
        if genera_password:
            data['password'] = random_password()

        try:
            return self.service.users().insert(body=data).execute(), data.get('password')
        except HttpError as e:
            raise ValueError("Errore: %s" % e._get_reason())

    def update_user(self, email, data, genera_password=False):
        from anagrafica.utils import random_password
        if genera_password:
            data['password'] = random_password()

        try:
            return self.service.users().update(userKey=email, body=data).execute(), data.get('password')
        except HttpError as e:
            raise ValueError("Errore: %s" % e._get_reason())


gsuite = GsuiteLib(GSUITE_CONF)


if __name__ == '__main__':

    from jorvik.settings import GSUITE_CONF

    gsuite = GsuiteLib(GSUITE_CONF)

    gsuite.init_service('directory_v1')

    print("Test reading users")
    users = gsuite.list_users(limit=10)
    for user in users:
        print('{0} ({1})'.format(user['primaryEmail'],
                                 user['name']['fullName']))

    print("Test creating user")
    data = dict(primaryEmail='foobar@{0}'.format(gsuite.base_domain),
                name=dict(givenName='Foo', familyName='Bar', fullName='Foo Bar'),
                password="foobar123")

    user, password = gsuite.new_user(data)
    print("User created with password %s" % password)

    print("Listing again")
    users = gsuite.list_users(limit=10)
    for user in users:
        print('{0} ({1})'.format(user['primaryEmail'],
                                 user['name']['fullName']))
