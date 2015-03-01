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
    url(r'^admin/', include(admin.site.urls)),
)

