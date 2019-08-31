from django.conf.urls import url
from . import viste


app_label = 'autoparco'
urlpatterns = [
    url(r'^(P<pk>.*)/$', viste.veicoli_autoparco),
    url(r'^modifica/(?P<pk>.*)/$', viste.veicoli_autoparco_modifica_o_nuovo),
    url(r'^nuovo/$', viste.veicoli_autoparco_modifica_o_nuovo),
]
