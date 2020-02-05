from django.conf.urls import url

from ufficio_soci.viste import verifica_tesserino
from base import viste


app_label = 'informazioni'
urlpatterns = [
    url(r'^$', viste.informazioni, name='index'),
    url(r'^statistiche/$', viste.informazioni_statistiche),
    url(r'^aggiornamenti/$', viste.informazioni_aggiornamenti),
    url(r'^sicurezza/$', viste.informazioni_sicurezza),
    url(r'^condizioni/$', viste.informazioni_condizioni, name='condizioni'),
    url(r'^cookie/$', viste.informazioni_cookie, name='cookie'),
    url(r'^cookie/imposta/$', viste.imposta_cookie, name='imposta_cookie'),
    url(r'^sedi/$', viste.informazioni_sedi),
    url(r'^sedi/(?P<slug>.*)/$', viste.informazioni_sede),
    url(r'^formazione/$', viste.formazione),
    url(r'^browser-supportati/$', viste.browser_supportati, name='browser_supportati'),
    url(r'^verifica-tesserino/$', verifica_tesserino, name='verifica_tesserino'),
]
