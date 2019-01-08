"""
Queste sono le impostazioni di Django per il progetto Jorvik.

Informazioni sul file:  https://docs.djangoproject.com/en/1.7/topics/settings/
Documentazione config.: https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from django.core.urlresolvers import reverse_lazy

from api.settings import OAUTH2_PROVIDER

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os

from datetime import timedelta, date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Deployment: https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Elenca le applicazioni installate da abilitare

INSTALLED_APPS = [
    'jorvik',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # Librerie terze
    'nocaptcha_recaptcha',
    'oauth2_provider',
    'corsheaders',
    'mptt',
    # Moduli interni
    'base',
    'autenticazione',
    'anagrafica',
    'attivita',
    'curriculum',
    'gruppi',
    'ufficio_soci',
    'veicoli',
    'social',
    'posta',
    'sangue',
    'static_page',
    'formazione',
    'bootstrap3',
    'django_countries',
    'autocomplete_light',
    'django_extensions',
    'loginas',
    'django_cron',
    'django.contrib.humanize',
    'django_gravatar',
    'centrale_operativa',
    'compressor',
    'easy_thumbnails',
    'gestione_file',
    'segmenti',
    'articoli',
    'filer',
    'ckeditor',
    'ckeditor_filebrowser_filer',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'otp_yubikey',
    'two_factor',
    'rest_framework',
]


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Cronjob attivi
CRON_CLASSES = [
    "base.cron.CronCancellaFileScaduti",
    "base.cron.CronApprovaNegaAuto",
    "base.cron.CronRichiesteInAttesa",
    "base.cron.PulisciAspirantiVolontari",
    "anagrafica.cron.CronReportComitati",
    "centrale_operativa.cron.CronCancellaCoturniInvalidi"
]

# Classi middleware (intercetta & computa)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
    'autenticazione.two_factor.middleware.Require2FA',
    'corsheaders.middleware.CorsMiddleware',
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
GENERAL_CONF_FILE = 'config/general.cnf' if os.path.isfile('config/general.cnf') else 'config/general.cnf.sample'
CELERY_CONF_FILE = 'config/celery.cnf' if os.path.isfile('config/celery.cnf') else 'config/celery.cnf.sample'

# MySQL
MYSQL_CONF = configparser.ConfigParser()
MYSQL_CONF.read(MYSQL_CONF_FILE)

# PGSQL
PGSQL_CONF = configparser.ConfigParser()
PGSQL_CONF.read(PGSQL_CONF_FILE)

# Configurazione debug e produzione
DEBUG_CONF = configparser.ConfigParser()
DEBUG_CONF.read(DEBUG_CONF_FILE)
DEBUG = DEBUG_CONF.getboolean('debug', 'debug')
SECRET_KEY = DEBUG_CONF.get('production', 'secret_key')
JORVIK_LOG_FILE = DEBUG_CONF.get('debug', 'debug_log', fallback=os.path.join('..', 'log', 'debug.log'))
JORVIK_LOG = os.path.join(BASE_DIR, JORVIK_LOG_FILE)

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

LOGIN_URL = reverse_lazy('two_factor:login')
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/utente/'
TWO_FACTOR_PROFILE = reverse_lazy('two_factor:profile')
TWO_FACTOR_SESSIONE_SCADUTA = '/scaduta/'
TWO_FACTOR_PUBLIC = (
    TWO_FACTOR_PROFILE, LOGOUT_URL, TWO_FACTOR_SESSIONE_SCADUTA, LOGIN_URL
)
TWO_FACTOR_SESSION_DURATA = DEBUG_CONF.getint('production', 'TWO_FACTOR_SESSION_DURATA', fallback=120)
SESSION_COOKIE_PATH = '/'

GENERAL_CONF = configparser.ConfigParser()
GENERAL_CONF.read(GENERAL_CONF_FILE)

CELERY_CONF = configparser.ConfigParser()
CELERY_CONF.read(CELERY_CONF_FILE)

# Driver per i test funzionali
DRIVER_WEB = 'firefox'

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

POSTA_LOG_DEBUG = EMAIL_CONF.getboolean('email', 'log_debug', fallback=True)

DEFAULT_FROM_EMAIL = 'Gaia <noreply@gaia.cri.it>'
GRAVATAR_DEFAULT_IMAGE = 'identicon'

# Configurazione media
MEDIA_CONF = configparser.ConfigParser()
MEDIA_CONF.read(MEDIA_CONF_FILE)
MEDIA_ROOT = MEDIA_CONF.get('media', 'media_root')
MEDIA_URL = MEDIA_CONF.get('media', 'media_url')
STATIC_ROOT = MEDIA_CONF.get('static', 'static_root', fallback='assets/')
STATIC_URL = MEDIA_CONF.get('static', 'static_url', fallback='/assets/')

# Driver per i test funzionali
SELENIUM_DRIVER = DEBUG_CONF.get('test', 'driver', fallback='firefox')
SELENIUM_BROWSER = DEBUG_CONF.get('test', 'browser', fallback='firefox')
SELENIUM_URL = DEBUG_CONF.get('test', 'url', fallback=None)

host = "%s" % (DEBUG_CONF.get('production', 'host'),)
if host == 'localhost':
    ALLOWED_HOSTS = ['*']
else:
    www_host = "www.%s" % (host,)
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', host, www_host]

# Permetti gateway o load balancer
gateway = DEBUG_CONF.get('production', 'gateway', fallback='')
if gateway:
    # TODO usare X-Forward-IP
    ALLOWED_HOSTS.append(gateway)

# Configurazione dei servizi API
APIS_CONF = configparser.ConfigParser()
APIS_CONF.read(APIS_CONF_FILE)
GOOGLE_KEY = APIS_CONF.get('google', 'api_key', fallback=os.environ.get("GOOGLE_KEY"))
DOMPDF_ENDPOINT = APIS_CONF.get('dompdf', 'endpoint',
                                fallback='')

DESTINATARI_REPORT = ['sviluppo@cri.it', 'info@gaia.cri.it']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': JORVIK_LOG,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'posta': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "jorvik.context_processors.settings",
            ),
            "debug": DEBUG_CONF.getboolean('debug', 'debug')

        },
    },
]

BOOTSTRAP3 = {
    'field_renderers': {
        'default': 'base.datetime.DateTimeFieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}

THUMBNAIL_BASEDIR = 'thumbnails'
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

FILER_CANONICAL_URL = 'sharing/'
FILER_IMAGE_FIELD = 'gestione_file.fields.CampoImmagineFiler'
FILER_FILE_FIELD = 'gestione_file.fields.CampoDocumentoFiler'
FILER_FILE_MODELS = (
    'gestione_file.models.Immagine',
    'gestione_file.models.Documento',
)
GESTIONE_FILE_PAGINAZIONE = 50

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            [
                'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft',
                'JustifyCenter', 'JustifyRight', 'JustifyBlock'
            ],
            ['Format', '-', 'Table'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['FilerImage'],
            ['Embed']
        ],
        'extraPlugins': 'filerimage,embed',
        'removePlugins': 'image'
    },
}

CKEDITOR_FILEBROWSER_USE_THUMBNAILOPTIONS_ONLY = True
CKEDITOR_FILEBROWSER_USE_CANONICAL_FOR_THUMBNAILS = '/documenti/immagine/'

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

NORECAPTCHA_SITE_KEY = APIS_CONF.get('nocaptcha', 'site_key', fallback=os.environ.get('NORECAPTCHA_SECRET_KEY'))
NORECAPTCHA_SECRET_KEY = APIS_CONF.get('nocaptcha', 'secret_key', fallback=os.environ.get('NORECAPTCHA_SITE_KEY'))

SCADENZA_AUTORIZZAZIONE_AUTOMATICA = GENERAL_CONF.getint('autorizzazioni', 'giorni', fallback=30)
DATA_AVVIO_TRASFERIMENTI_AUTO = date(2017, 1, 18)

if os.environ.get('ENABLE_TEST_APPS', False):
    INSTALLED_APPS.append('segmenti.segmenti_test')

CAN_LOGIN_AS = lambda request, target_user: request.user.is_superuser or request.user.groups.filter(name='loginas').exists()
LOGOUT_URL = reverse_lazy('logout')
LOGINAS_LOGOUT_REDIRECT_URL = reverse_lazy('admin:autenticazione_utenza_changelist')
LOGOUT_REDIRECT_URL = '/'

# Entro questa finestra temporale i corsi sono visibili agli aspiranti e si possono iscrivere autonomamente
FORMAZIONE_FINESTRA_CORSI_INIZIATI = 7
# Durata delli inviti ai corsi base
FORMAZIONE_VALIDITA_INVITI = 7

POSTA_MASSIVA_TIMEOUT = 30
DATE_FORMAT = '%d/%m/%Y'

CORS_ORIGIN_ALLOW_ALL = True

# API: permetti autenticazione tramite OAuth 2.0
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

from django.utils.translation import ugettext_lazy as _

COUNTRIES_OVERRIDE = {
    'KS': _('Kosovo'),
}
