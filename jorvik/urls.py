"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse

print("Getto gli URLS")
urlpatterns = patterns('',

    url(r'^$', 'base.viste.index'),

    url(r'^manutenzione/$', 'base.viste.manutenzione'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'base_login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'base_logout.html'}),
    url('^', include('django.contrib.auth.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

