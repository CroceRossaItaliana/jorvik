from django.conf.urls import url
from .. import viste as v

app_label = 'evento'
urlpatterns = [
        url(r'^(?P<pk>[0-9]+)/info$', v.evento_scheda_info, name='info'),
        url(r'^(?P<pk>[0-9]+)/modifica$', v.evento_scheda_modifica, name='modifica'),
        url(r'^(?P<pk>[0-9]+)/mappa$', v.evento_scheda_mappa, name='mappa'),
        url(r'^(?P<pk>[0-9]+)/attiva$', v.evento_attiva, name='attiva'),
        url(r'^(?P<pk>[0-9]+)/annulla$', v.evento_annulla, name='annulla'),
        url(r'^(?P<pk>[0-9]+)/position/change', v.formazione_evento_position_change, name='position_change'),
]
