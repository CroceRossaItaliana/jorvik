"""
Queste sono le impostazioni di Django per il progetto Jorvik.

Informazioni sul file:  https://docs.djangoproject.com/en/1.7/topics/settings/
Documentazione config.: https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from django.template.base import add_to_builtins

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Deployment: https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Elenca le applicazioni installate da abilitare

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # Librerie terze
    # 'oauth2_provider',
    'rest_framework',
    'mptt',
    'safedelete',
    # Moduli interni
    'base',
    'autenticazione',
    'anagrafica',
    'attivita',
    'curriculum',
    'gruppi',
    'patenti',
    'ufficio_soci',
    'veicoli',
    'social',
    'posta',
    'sangue',
    'formazione',
    'bootstrap3',
    'django_countries',
    'autocomplete_light',
    'django_extensions',
    'loginas',
    'sorl.thumbnail',
)

# Classi middleware (intercetta & computa)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSOR = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

# Imposta anagrafica.Utenza come modello di autenticazione
AUTH_USER_MODEL = 'autenticazione.Utenza'

# Configurazione URL
ROOT_URLCONF = 'jorvik.urls'

# Applicazione per il deployment tramite WSGI
WSGI_APPLICATION = 'jorvik.wsgi.application'

# Usa pickle come serializzatore
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
MYSQL_CONF_FILE = 'config/mysql.cnf' if os.path.isfile('config/mysql.cnf') else 'config/mysql.cnf.sample'
PGSQL_CONF_FILE = 'config/pgsql.cnf' if os.path.isfile('config/pgsql.cnf') else 'config/pgsql.cnf.sample'
EMAIL_CONF_FILE = 'config/email.cnf' if os.path.isfile('config/email.cnf') else 'config/email.cnf.sample'
MEDIA_CONF_FILE = 'config/media.cnf' if os.path.isfile('config/media.cnf') else 'config/media.cnf.sample'
DEBUG_CONF_FILE = 'config/debug.cnf' if os.path.isfile('config/debug.cnf') else 'config/debug.cnf.sample'
APIS_CONF_FILE = 'config/apis.cnf' if os.path.isfile('config/apis.cnf') else 'config/apis.cnf.sample'

# MySQL
MYSQL_CONF = configparser.ConfigParser()
MYSQL_CONF.read(MYSQL_CONF_FILE)

# PGSQL
PGSQL_CONF = configparser.ConfigParser()
PGSQL_CONF.read(PGSQL_CONF_FILE)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'autenticazione.retro.RetroGaiaHasher'
)


DATABASES = {
    'default': {
        #'TEST': {
        #    'NAME': 'test_jorvik',
        #},
        #'ENGINE': 'django.contrib.gis.db.backends.mysql',
        #'OPTIONS': {
        #    'read_default_file': MYSQL_CONF_FILE,
        #    'init_command': 'SET storage_engine=MyISAM',
        #},
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': PGSQL_CONF.get('client', 'database', fallback='jorvik'),
        'USER': PGSQL_CONF.get('client', 'user', fallback='jorvik'),
        'PASSWORD': PGSQL_CONF.get('client', 'password', fallback='jorvik'),
        'HOST': PGSQL_CONF.get('client', 'host', fallback='localhost'),
        'PORT': PGSQL_CONF.get('client', 'port', fallback='5432'),
    }
}

# Internazionalizzazione
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'it-it'
TIME_ZONE = 'CET'
USE_I18N = True
USE_L10N = True
USE_TZ = False

SITE_ID = 1


# File statici (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

TEMPLATE_DIRS = (
    'base/templates',
    os.path.join(BASE_DIR,  'templates'),
)

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/utente/'
SESSION_COOKIE_PATH = '/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

# Configurazione E-mail
EMAIL_CONF = configparser.ConfigParser()
EMAIL_CONF.read(EMAIL_CONF_FILE)
EMAIL_BACKEND = EMAIL_CONF.get('email', 'backend')
EMAIL_FILE_PATH = EMAIL_CONF.get('email', 'file_path')
EMAIL_HOST = EMAIL_CONF.get('email', 'host')
EMAIL_PORT = EMAIL_CONF.get('email', 'port')
EMAIL_HOST_USER = EMAIL_CONF.get('email', 'username')
EMAIL_HOST_PASSWORD = EMAIL_CONF.get('email', 'password')
EMAIL_USE_SSL = EMAIL_CONF.getboolean('email', 'ssl')
EMAIL_USE_TLS = EMAIL_CONF.getboolean('email', 'tls')
EMAIL_SSL_KEYFILE = EMAIL_CONF.get('email', 'ssl_keyfile')
EMAIL_SSL_CERTFILE = EMAIL_CONF.get('email', 'ssl_certfile')

DEFAULT_FROM_EMAIL = 'Gaia <noreply@gaia.cri.it>'

# Configurazione media
MEDIA_CONF = configparser.ConfigParser()
MEDIA_CONF.read(MEDIA_CONF_FILE)
MEDIA_ROOT = MEDIA_CONF.get('media', 'media_root')
MEDIA_URL = MEDIA_CONF.get('media', 'media_url')
STATIC_ROOT = MEDIA_CONF.get('static', 'static_root', fallback='assets/')
STATIC_URL = MEDIA_CONF.get('static', 'static_url', fallback='/assets/')

# Configurazione debug e produzione
DEBUG_CONF = configparser.ConfigParser()
DEBUG_CONF.read(DEBUG_CONF_FILE)
DEBUG = DEBUG_CONF.getboolean('debug', 'debug')
TEMPLATE_DEBUG = DEBUG_CONF.getboolean('debug', 'debug')
SECRET_KEY = DEBUG_CONF.get('production', 'secret_key')
ALLOWED_HOST = ['localhost', '127.0.0.1', DEBUG_CONF.get('production', 'host')]

# Configurazione dei servizi API
APIS_CONF = configparser.ConfigParser()
APIS_CONF.read(APIS_CONF_FILE)
GOOGLE_KEY = APIS_CONF.get('google', 'api_key')
DOMPDF_ENDPOINT = APIS_CONF.get('dompdf', 'endpoint',
                                fallback='http://pdf-server.alacriter.uk.92-222-162-128.alacriter.uk/render/www/render.php')
