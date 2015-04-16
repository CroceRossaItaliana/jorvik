"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse

print("Getto gli URLS")
urlpatterns = patterns('',

    # Home page!
    url(r'^$', 'base.viste.index'),

    # Moduli di registrazione
    url(r'^registrati/(?P<tipo>\w+)/conferma/$', 'anagrafica.viste.registrati_conferma'),
    url(r'^registrati/(?P<tipo>\w+)/$', 'anagrafica.viste.registrati'),
    url(r'^registrati/(?P<tipo>\w+)/(?P<step>\w+)/$', 'anagrafica.viste.registrati'),

    # Modalita' manutenzione
    url(r'^manutenzione/$', 'base.viste.manutenzione'),

    # Login e logout
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'base_login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'base_logout.html'}),
    url('^', include('django.contrib.auth.urls')),

    # Modulo di recupero password
    url(r'^recupera-password/$', 'base.viste.recupera_password'),

    # Informazioni
    url(r'^informazioni/$', 'base.viste.informazioni'),
    url(r'^informazioni/aggiornamenti/$', 'base.viste.aggiornamenti'),
    url(r'^informazioni/sicurezza/$', 'base.viste.sicurezza'),
    url(r'^informazioni/condizioni/$', 'base.viste.condizioni'),

    # Amministrazione
    url(r'^admin/', include(admin.site.urls)),

    # OAuth 2.0
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

