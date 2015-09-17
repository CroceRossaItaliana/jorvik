"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done
from django.shortcuts import redirect
from anagrafica.forms import ModuloModificaPassword
from autenticazione.funzioni import pagina_privata, pagina_privata_no_cambio_firma
from jorvik.settings import MEDIA_ROOT

handler404 = 'base.errori.non_trovato'

urlpatterns = [

    # Home page!
    url(r'^$', 'base.viste.index'),

    # Moduli di registrazione
    url(r'^registrati/(?P<tipo>\w+)/conferma/$', 'anagrafica.viste.registrati_conferma'),
    url(r'^registrati/(?P<tipo>\w+)/$', 'anagrafica.viste.registrati'),
    url(r'^registrati/(?P<tipo>\w+)/(?P<step>\w+)/$', 'anagrafica.viste.registrati'),

    # Modalita' manutenzione
    url(r'^manutenzione/$', 'base.viste.manutenzione'),

    # Pagina di errore
    url(r'^errore/404/$', 'base.errori.non_trovato'),
    url(r'^errore/orfano/$', 'base.errori.orfano'),
    url(r'^errore/permessi/$', 'base.errori.permessi'),

    # Login e logout
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'base_login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'base_logout.html'}),
    url('^', include('django.contrib.auth.urls')),

    # Modulo di recupero password
    url(r'^recupera-password/$', 'base.viste.recupera_password'),

    # Informazioni
    url(r'^informazioni/$', 'base.viste.informazioni'),
    url(r'^informazioni/aggiornamenti/$', 'base.viste.informazioni_aggiornamenti'),
    url(r'^informazioni/sicurezza/$', 'base.viste.informazioni_sicurezza'),
    url(r'^informazioni/condizioni/$', 'base.viste.informazioni_condizioni'),
    url(r'^informazioni/sedi/$', 'base.viste.informazioni_sedi'),
    url(r'^informazioni/sedi/(?P<slug>.*)/$', 'base.viste.informazioni_sede'),

    # Applicazioni
    url(r'^utente/$', 'anagrafica.viste.utente'),
    url(r'^utente/anagrafica/$', 'anagrafica.viste.utente_anagrafica'),
    url(r'^utente/documenti/$', 'anagrafica.viste.utente_documenti'),
    url(r'^utente/documenti/zip/$', 'anagrafica.viste.utente_documenti_zip'),
    url(r'^utente/documenti/cancella/(?P<pk>.*)/$', 'anagrafica.viste.utente_documenti_cancella'),
    url(r'^utente/storico/$', 'anagrafica.viste.utente_storico'),
    url(r'^utente/contatti/$', 'anagrafica.viste.utente_contatti'),
    url(r'^utente/cambia-password/?$', pagina_privata_no_cambio_firma(password_change), {
        "template_name": "anagrafica_utente_cambia_password.html",
        "password_change_form": ModuloModificaPassword,
        "post_change_redirect": "/utente/cambia-password/fatto/"
    }),
    url(r'^utente/cambia-password/fatto/$', pagina_privata_no_cambio_firma(password_change_done), {
        "template_name": "anagrafica_utente_cambia_password_fatto.html",
    }),

    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/(?P<messaggio_id>\d+)/', 'posta.viste.posta'),
    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/', 'posta.viste.posta'),
    url(r'^posta/(?P<direzione>[\w\-]+)/', 'posta.viste.posta'),
    url(r'^posta/', 'posta.viste.posta_home'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {"document_root": MEDIA_ROOT}),

    # Amministrazione
    url(r'^admin/', include(admin.site.urls)),

    # OAuth 2.0
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
