from django.conf.urls import url

from centrale_operativa import viste as co_views
from gruppi import viste as gruppi_views
from . import views


app_label = 'so'
urlpatterns = [
    url(r'^$', views.servizio, name='index'),

    # Aree
    url(r'^aree/$', views.so_aree, name='aree'),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/$', views.so_aree_sede, name='aree_sede'),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/responsabili/$', views.so_aree_sede_area_responsabili, name='sede_area_responsabili'),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/cancella/$', views.so_aree_sede_area_cancella, name='sede_area_cancella'),

    # Organizza
    url(r'^organizza/$', views.so_organizza, name='organizza'),
    url(r'^organizza/(?P<pk>[0-9\-]+)/referenti/$', views.so_referenti, {"nuova": True}, name='organizza_referenti'),
    url(r'^organizza/(?P<pk>[0-9\-]+)/fatto/$', views.so_organizza_fatto, name='organizza_referenti_fatto'),

    # Gestisci
    url(r'^gestisci/$', views.so_gestisci, {"stato": "aperte"}, name='gestisci'),
    url(r'^gestisci/chiuse/$', views.so_gestisci, {"stato": "chiuse"}, name='gestisci_chiuse'),

    # Calendario
    url(r'^calendario/$', views.so_calendario, name='calendario'),
    url(r'^calendario/(?P<inizio>[0-9\-]+)/(?P<fine>[0-9\-]+)/$', views.so_calendario, name='calendario_con_range'),

    # Storico
    url(r'^storico/$', views.so_storico, name='storico'),
    url(r'^storico/excel/$', views.so_storico_excel, name='storico_excel'),
    url(r'^statistiche/$', views.so_statistiche, name='statistiche'),

    # Gruppi
    url(r'^gruppo/$', gruppi_views.so_gruppo),
    url(r'^gruppi/$', gruppi_views.so_gruppi),
    url(r'^gruppi/(?P<pk>[0-9]+)/$', gruppi_views.so_gruppi_gruppo),
    url(r'^gruppi/(?P<pk>[0-9]+)/iscriviti/$', gruppi_views.so_gruppi_gruppo_iscriviti),
    url(r'^gruppi/(?P<pk>[0-9]+)/espelli/(?P<persona_pk>[0-9]+)/$', gruppi_views.so_gruppi_gruppo_espelli),
    url(r'^gruppi/(?P<pk>[0-9]+)/abbandona/$', gruppi_views.so_gruppi_gruppo_abbandona),
    url(r'^gruppi/(?P<pk>[0-9]+)/elimina/$', gruppi_views.so_gruppi_gruppo_elimina),
    url(r'^gruppi/(?P<pk>[0-9]+)/elimina_conferma/$', gruppi_views.so_gruppi_gruppo_elimina_conferma),

    # Reperibilita
    url(r'^reperibilita/$', co_views.so_reperibilita),
    url(r'^reperibilita/(?P<reperibilita_pk>[0-9]+)/cancella/$', co_views.so_reperibilita_cancella),

    # Scheda
    url(r'^scheda/(?P<pk>[0-9]+)/$', views.so_scheda_informazioni),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella-gruppo/$', views.so_scheda_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella/$', views.so_scheda_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/mappa/$', views.so_scheda_mappa),
    url(r'^scheda/(?P<pk>[0-9]+)/partecipanti/$', views.so_scheda_partecipanti),
    url(r'^scheda/(?P<pk>[0-9]+)/modifica/$', views.so_scheda_informazioni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/riapri/$', views.so_riapri),
    url(r'^scheda/(?P<pk>[0-9]+)/referenti/$', views.so_referenti),
    url(r'^scheda/(?P<pk>[0-9]+)/report/$', views.so_scheda_report),

    # Turni
    url(r'^scheda/(?P<pk>[0-9]+)/turni/$', views.so_scheda_turni),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<pagina>[0-9]+)/$', views.so_scheda_turni),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipa/$', views.so_scheda_turni_partecipa),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/ritirati/$', views.so_scheda_turni_ritirati),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipanti/$', views.so_scheda_turni_partecipanti),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/link-permanente/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_link_permanente),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/cancella/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_turno_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/$', views.so_scheda_turni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/nuovo/$', views.so_scheda_turni_nuovo),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/(?P<pagina>[0-9]+)/$', views.so_scheda_turni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/link-permanente/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_modifica_link_permanente),

    # Partecipazione
    url(r'^scheda/(?P<pk>[0-9]+)/partecipazione/(?P<partecipazione_pk>[0-9]+)/cancella/$', views.so_scheda_partecipazione_cancella),
]
