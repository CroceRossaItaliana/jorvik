from django.conf.urls import url

from .. import viste


app_label = 'autorizzazioni'
urlpatterns = [
    url(r'^$', viste.autorizzazioni, name='aperte'),
    url(r'^storico/$', viste.autorizzazioni_storico, name='storico'),
    url(r'^(?P<content_type_pk>[0-9]+)/$', viste.autorizzazioni, name='dettaglio'),
    url(r'^(?P<pk>[0-9]+)/concedi/$', viste.autorizzazione_concedi, name='concedi'),
    url(r'^(?P<pk>[0-9]+)/qualifica-presa-visione/$', viste.autorizzazione_qualifica_presa_visione, name='qualifica_presa_visione'),
    url(r'^(?P<pk>[0-9]+)/nega/$', viste.autorizzazione_nega, name='nega'),
]
