"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jorvik.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    #url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    #url(r'^api-autenticazione/', include('rest_framework.urls', namespace='rest_framework')),

)
