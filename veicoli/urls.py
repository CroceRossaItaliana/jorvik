from django.conf.urls import url
from . import viste


app_label = 'veicoli'
urlpatterns = [
    url(r'^$', viste.veicoli),
    url(r'^elenco/$', viste.veicoli_elenco),
    url(r'^autoparchi/$', viste.veicoli_autoparchi),
    url(r'^autoparco/elenco/(?P<autoparco>.*)/$', viste.veicoli_elenco_autoparco),
    url(r'^(P<pk>.*)/$', viste.veicoli_veicolo),
    url(r'^nuovo/$', viste.veicoli_veicolo_modifica_o_nuovo),
    url(r'^modifica/(?P<pk>.*)/$', viste.veicoli_veicolo_modifica_o_nuovo),
    url(r'^manutenzioni/(?P<veicolo>.*)/$', viste.veicoli_manutenzione),
    url(r'^manutenzione/(?P<manutenzione>.*)/modifica/$', viste.veicoli_modifica_manutenzione),
    url(r'^rifornimento/(?P<rifornimento>.*)/modifica/$', viste.veicoli_modifica_rifornimento),
    url(r'^rifornimenti/(?P<veicolo>.*)/$', viste.veicoli_rifornimento),
    url(r'^fermi-tecnici/(?P<veicolo>.*)/$', viste.veicoli_fermo_tecnico),
    url(r'^termina/fermo-tecnico/(?P<fermo>.*)/$', viste.veicoli_termina_fermo_tecnico),
    url(r'^(?P<veicolo>.*)/collocazioni/$', viste.veicoli_collocazioni),
    url(r'^dettagli/(?P<veicolo>.*)/$', viste.veicolo_dettagli),
]
