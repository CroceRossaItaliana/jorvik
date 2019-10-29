from django.conf.urls import url

from centrale_operativa import viste as co_views
from gruppi import viste as gruppi_views
from . import viste


app_label = 'attivita'
urlpatterns = [
    url(r'^$', viste.attivita),
    url(r'^aree/$', viste.attivita_aree),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/$', viste.attivita_aree_sede),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/cancella/$', viste.attivita_aree_sede_area_cancella),
    url(r'^aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/responsabili/$', viste.attivita_aree_sede_area_responsabili),
    url(r'^organizza/$', viste.attivita_organizza),
    url(r'^organizza/(?P<pk>[0-9\-]+)/referenti/$', viste.attivita_referenti, {"nuova": True}),
    url(r'^organizza/(?P<pk>[0-9\-]+)/fatto/$', viste.attivita_organizza_fatto),
    url(r'^statistiche/$', viste.attivita_statistiche),
    url(r'^gestisci/$', viste.attivita_gestisci, {"stato": "aperte"}),
    url(r'^gestisci/chiuse/$', viste.attivita_gestisci, {"stato": "chiuse"}),
    url(r'^calendario/$', viste.attivita_calendario),
    url(r'^calendario/(?P<inizio>[0-9\-]+)/(?P<fine>[0-9\-]+)/$', viste.attivita_calendario),
    url(r'^storico/$', viste.attivita_storico),
    url(r'^storico/excel/$', viste.attivita_storico_excel),

    url(r'^gruppo/$', gruppi_views.attivita_gruppo),
    url(r'^gruppi/$', gruppi_views.attivita_gruppi),
    url(r'^gruppi/(?P<pk>[0-9]+)/$', gruppi_views.attivita_gruppi_gruppo),
    url(r'^gruppi/(?P<pk>[0-9]+)/iscriviti/$', gruppi_views.attivita_gruppi_gruppo_iscriviti),
    url(r'^gruppi/(?P<pk>[0-9]+)/espelli/(?P<persona_pk>[0-9]+)/$', gruppi_views.attivita_gruppi_gruppo_espelli),
    url(r'^gruppi/(?P<pk>[0-9]+)/abbandona/$', gruppi_views.attivita_gruppi_gruppo_abbandona),
    url(r'^gruppi/(?P<pk>[0-9]+)/elimina/$', gruppi_views.attivita_gruppi_gruppo_elimina),
    url(r'^gruppi/(?P<pk>[0-9]+)/elimina_conferma/$', gruppi_views.attivita_gruppi_gruppo_elimina_conferma),

    url(r'^reperibilita/$', co_views.attivita_reperibilita),
    url(r'^reperibilita/(?P<reperibilita_pk>[0-9]+)/cancella/$', co_views.attivita_reperibilita_cancella),

    url(r'^scheda/(?P<pk>[0-9]+)/$', viste.attivita_scheda_informazioni),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella-gruppo/$', viste.attivita_scheda_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella/$', viste.attivita_scheda_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/mappa/$', viste.attivita_scheda_mappa),
    url(r'^scheda/(?P<pk>[0-9]+)/partecipanti/$', viste.attivita_scheda_partecipanti),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/$', viste.attivita_scheda_turni),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<pagina>[0-9]+)/$', viste.attivita_scheda_turni),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipa/$', viste.attivita_scheda_turni_partecipa),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/ritirati/$', viste.attivita_scheda_turni_ritirati),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipanti/$', viste.attivita_scheda_turni_partecipanti),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/link-permanente/(?P<turno_pk>[0-9]+)/$', viste.attivita_scheda_turni_link_permanente),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/cancella/(?P<turno_pk>[0-9]+)/$', viste.attivita_scheda_turni_turno_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/$', viste.attivita_scheda_turni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/nuovo/$', viste.attivita_scheda_turni_nuovo),
    url(r'^scheda/(?P<pk>[0-9]+)/partecipazione/(?P<partecipazione_pk>[0-9]+)/cancella/$', viste.attivita_scheda_partecipazione_cancella),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/(?P<pagina>[0-9]+)/$', viste.attivita_scheda_turni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/link-permanente/(?P<turno_pk>[0-9]+)/$', viste.attivita_scheda_turni_modifica_link_permanente),
    url(r'^scheda/(?P<pk>[0-9]+)/modifica/$', viste.attivita_scheda_informazioni_modifica),
    url(r'^scheda/(?P<pk>[0-9]+)/riapri/$', viste.attivita_riapri),
    url(r'^scheda/(?P<pk>[0-9]+)/referenti/$', viste.attivita_referenti),
    url(r'^scheda/(?P<pk>[0-9]+)/report/$', viste.attivita_scheda_report),
    # Servizi
    url(r'^servizio/organizza/$', viste.servizio_organizza),
    url(r'^servizio/gestisci/$', viste.servizio_gestisci, {"stato": "aperte"}),
    url(r'^servizio/gestisci/chiuse/$', viste.servizio_gestisci, {"stato": "chiuse"}),
    url(r'^servizio/organizza/(?P<pk>[a-zA-Z0-9\-]+)/referenti/$', viste.servizi_referenti, {"nuova": True}),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica$', viste.servizio_scheda_informazioni_modifica),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/accesso$', viste.servizio_scheda_informazioni_modifica_accesso, name='accesso'),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/specifiche', viste.servizio_scheda_informazioni_modifica_specifiche, name='specifiche'),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/presentazione', viste.servizio_scheda_informazioni_modifica_presentazione),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/contatti', viste.servizio_scheda_informazioni_modifica_contatti),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/convenzioni', viste.servizio_scheda_informazioni_modifica_convenzioni),
    url(r'^servizio/scheda/(?P<pk>[a-zA-Z0-9\-]+)/modifica/servizi$', viste.servizio_modifica_servizi_standard),
]
