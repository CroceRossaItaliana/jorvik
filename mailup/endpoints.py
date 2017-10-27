MAIN_URL = 'https://services.mailup.com'
VERSION = 'v1.1'
ENDPOINTS = {
    'logon': '{}{}'.format(MAIN_URL, '/Authorization/OAuth/LogOn'),
    'token': '{}{}'.format(MAIN_URL, '/Authorization/OAuth/Token'),
    'read_lists': '{}/API/{}/Rest{}'.format(MAIN_URL, VERSION, '/ConsoleService.svc/Console/List'),
    'create_list': '{}/API/{}/Rest{}'.format(MAIN_URL, VERSION, '/ConsoleService.svc/Console/List'),
    'read_recipients': '{}/API/{}/Rest{}'.format(MAIN_URL, VERSION, '/ConsoleService.svc/Console/List/{}/Recipients/EmailOptins'),
}
