from django.conf.urls import url

from . import views


pk = "(?P<pk>[0-9]+)"

app_label = 'so'
urlpatterns = [
    url(r'^$', views.so_index, name='index'),

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
    # url(r'^gruppo/$', gruppi_views.attivita_gruppo, name='gruppo'),
    # url(r'^gruppi/$', gruppi_views.attivita_gruppi, name='gruppi'),
    # url(r'^gruppi/(?P<pk>[0-9]+)/$', gruppi_views.attivita_gruppi_gruppo, name='gruppi_gruppo'),
    # url(r'^gruppi/(?P<pk>[0-9]+)/iscriviti/$', gruppi_views.attivita_gruppi_gruppo_iscriviti),
    # url(r'^gruppi/(?P<pk>[0-9]+)/espelli/(?P<persona_pk>[0-9]+)/$', gruppi_views.attivita_gruppi_gruppo_espelli),
    # url(r'^gruppi/(?P<pk>[0-9]+)/abbandona/$', gruppi_views.attivita_gruppi_gruppo_abbandona),
    # url(r'^gruppi/(?P<pk>[0-9]+)/elimina/$', gruppi_views.attivita_gruppi_gruppo_elimina),
    # url(r'^gruppi/(?P<pk>[0-9]+)/elimina_conferma/$', gruppi_views.attivita_gruppi_gruppo_elimina_conferma),

    # Reperibilita
    url(r'^r/$', views.so_reperibilita, name='reperibilita'),
    url(r'^r/backup/$', views.so_reperibilita_backup, name='reperibilita_backup'),
    url(r'^r/%s/delete/$' % pk, views.so_reperibilita_cancella, name='reperibilita_cancella'),
    url(r'^r/%s/edit/$' % pk, views.so_reperibilita_edit, name='reperibilita_modifica'),

    # Scheda
    url(r'^scheda/(?P<pk>[0-9]+)/$', views.so_scheda_informazioni, name='scheda'),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella-gruppo/$', views.so_scheda_cancella, name='scheda_cancella_gruppo'),
    url(r'^scheda/(?P<pk>[0-9]+)/cancella/$', views.so_scheda_cancella, name='scheda_cancella'),
    url(r'^scheda/(?P<pk>[0-9]+)/mappa/$', views.so_scheda_mappa, name='scheda_mappa'),
    url(r'^scheda/(?P<pk>[0-9]+)/partecipanti/$', views.so_scheda_partecipanti, name='scheda_partecipanti'),
    url(r'^scheda/(?P<pk>[0-9]+)/modifica/$', views.so_scheda_informazioni_modifica, name='scheda_modifica'),
    url(r'^scheda/(?P<pk>[0-9]+)/riapri/$', views.so_riapri, name='scheda_riapri'),
    url(r'^scheda/(?P<pk>[0-9]+)/referenti/$', views.so_referenti, name='scheda_referenti'),
    url(r'^scheda/(?P<pk>[0-9]+)/report/$', views.so_scheda_report, name='report'),

    # Turni
    url(r'^scheda/(?P<pk>[0-9]+)/turni/$', views.so_scheda_turni, name='so_scheda_turni'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/nuovo/$', views.so_scheda_turni_nuovo, name='so_scheda_turni_nuovo'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<pagina>[0-9]+)/$', views.so_scheda_turni, name='so_scheda_turni_pagina'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipa/$', views.so_scheda_turni_partecipa, name='scheda_turni_partecipa'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/ritirati/$', views.so_scheda_turni_ritirati, name='scheda_turni_ritirati'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipanti/$', views.so_scheda_turni_partecipanti, name='scheda_turni_partecipanti'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/link-permanente/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_link_permanente, name='scheda_turni_link_permanente'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/cancella/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_turno_cancella, name='scheda_turni_cancella'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/$', views.so_scheda_turni_modifica, name='scheda_turni_modifica'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/(?P<pagina>[0-9]+)/$', views.so_scheda_turni_modifica, name='scheda_turni_modifica_pagina'),
    url(r'^scheda/(?P<pk>[0-9]+)/turni/modifica/link-permanente/(?P<turno_pk>[0-9]+)/$', views.so_scheda_turni_modifica_link_permanente, name='scheda_turni_modifica_link_permanente'),

    # Partecipazione
    url(r'^scheda/(?P<pk>[0-9]+)/partecipazione/(?P<partecipazione_pk>[0-9]+)/cancella/$', views.so_scheda_partecipazione_cancella, name='scheda_partecipazione_cancella'),

    # Mezzi e materiali
    url(r'^mm/$', views.so_mezzi, name='mezzi'),
    url(r'^mm/%s/edit/$' % pk, views.so_mezzo_modifica, name='mezzo_modifica'),
    url(r'^mm/%s/delete/$' % pk, views.so_mezzo_cancella, name='mezzo_cancella'),
]
