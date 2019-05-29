from django.conf.urls import url
from . import viste


app_label = 'centrale_operativa'
urlpatterns = [
    url(r'^$', viste.co),
    url(r'^reperibilita/$', viste.co_reperibilita),
    url(r'^poteri/$', viste.co_poteri),
    url(r'^poteri/(?P<part_pk>[0-9]+)/$', viste.co_poteri_switch),
    url(r'^turni/$', viste.co_turni),
    url(r'^turni/(?P<partecipazione_pk>[0-9]+)/monta/$', viste.co_turni_monta),
    url(r'^turni/(?P<partecipazione_pk>[0-9]+)/smonta/$', viste.co_turni_smonta),
]
