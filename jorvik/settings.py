"""
Queste sono le impostazioni di Django per il progetto Jorvik.

Informazioni sul file:  https://docs.djangoproject.com/en/1.7/topics/settings/
Documentazione config.: https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Deployment: https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# DA CAMBIARE IN PRODUZIONE
SECRET_KEY = 'nxt$3dhwh_k_@lh^)=^i^ra!$ty-vy1v=g7fptenicbiqqwaqt'

# DA CAMBIARE IN PRODUZIONE
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Elenca le applicazioni installate da abilitare

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # Librerie terze
    'oauth2_provider',
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
    'formazione',
    'bootstrap3',
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


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'jorvik',
        'TEST': {
            'NAME': 'test_jorvik',
        },
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': 'config/mysql.cnf',
            'init_command': 'SET storage_engine=MyISAM',
        },
    }
}

# Internazionalizzazione
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'it-it'
TIME_ZONE = 'CET'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# File statici (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/tmp'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}
