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
    # Moduli Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerie terze
    #'provider',
    #'provider.oauth2',
    'rest_framework',
    'mptt',

    # Moduli interni
    'base',
    'anagrafica',
    'social',
    'posta',
    'formazione',
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

# Imposta anagrafica.Utenza come modello di autenticazione
AUTH_USER_MODEL = 'anagrafica.Utenza'

# Configurazione URL
ROOT_URLCONF = 'jorvik.urls'

# Applicazione per il deployment tramite WSGI
WSGI_APPLICATION = 'jorvik.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/config/mysql.cnf',
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

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)