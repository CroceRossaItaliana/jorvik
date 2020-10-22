from django.conf.urls import url

from . import views


pk = "(?P<pk>[0-9]+)"

app_label = 'so'
urlpatterns = [
    url(r'^$', views.so_index, name='index'),

    # Datore Lavoro
    url(r'^ddl/$', views.utente_datore_di_lavoro, name='datore_di_lavoro'),
    url(r'^ddl/(?P<pk>.*)/modifica$', views.utente_datore_di_lavoro_modifica, name='datore_di_lavoro_modifica'),
    url(r'^ddl/(?P<pk>.*)/cancella$', views.utente_datore_di_lavoro_cancella, name='datore_di_lavoro_cancella'),

    # Organizza
    url(r'^organizza/$', views.so_organizza, name='organizza'),
    url(r'^organizza/(?P<pk>[0-9\-]+)/referenti/$', views.so_referenti, {"nuova": True}, name='organizza_referenti'),
    url(r'^organizza/(?P<pk>[0-9\-]+)/fatto/$', views.so_organizza_fatto, name='organizza_fatto'),

    # Gestisci servizi
    url(r'^servizi/$', views.so_gestisci, {"stato": "aperte"}, name='gestisci'),
    url(r'^servizi/chiusi/$', views.so_gestisci, {"stato": "chiuse"}, name='gestisci_chiuse'),

    # Calendario
    url(r'^calendario/$', views.so_calendario, name='calendario'),

    # Storico
    url(r'^storico/$', views.so_storico, name='storico'),
    url(r'^storico/excel/$', views.so_storico_excel, name='storico_excel'),
    url(r'^statistiche/$', views.so_statistiche, name='statistiche'),

    # Reperibilita
    url(r'^r/$', views.so_reperibilita, name='reperibilita'),
    url(r'^r/backup/$', views.so_reperibilita_backup, name='reperibilita_backup'),
    url(r'^r/%s/delete/$' % pk, views.so_reperibilita_cancella, name='reperibilita_cancella'),
    url(r'^r/%s/edit/$' % pk, views.so_reperibilita_edit, name='reperibilita_modifica'),

    # Servizio
    url(r'^servizio/%s/$' % pk, views.so_scheda_informazioni, name='servizio'),
    url(r'^servizio/%s/cancella/$' % pk, views.so_scheda_cancella, name='servizio_cancella'),
    url(r'^servizio/%s/mappa/$' % pk, views.so_scheda_mappa, name='servizio_mappa'),
    url(r'^servizio/%s/partecipanti/$' % pk, views.so_scheda_partecipanti, name='servizio_partecipanti'),
    url(r'^servizio/%s/modifica/$' % pk, views.so_scheda_informazioni_modifica, name='servizio_modifica'),
    url(r'^servizio/%s/conferma/$' % pk, views.so_scheda_conferma, name='servizio_conferma'),
    url(r'^servizio/%s/conferma/richiedi/$' % pk, views.so_scheda_richiedi_conferma, name='servizio_richiedi_conferma'),
    url(r'^servizio/%s/riapri/$' % pk, views.so_riapri, name='servizio_riapri'),
    url(r'^servizio/%s/referenti/$' % pk, views.so_referenti, name='servizio_referenti'),
    url(r'^servizio/%s/report/$' % pk, views.so_scheda_report, name='servizio_report'),
    url(r'^servizio/%s/attestati/$' % pk, views.so_scheda_attestati, name='servizio_attestati'),
    url(r'^servizio/%s/attestato/(?P<partecipazione_pk>[0-9]+)/$' % pk, views.so_scheda_scarica_attestato, name='servizio_scarica_attestato'),

    # Scheda Mezzi e Materiali
    url(r'^scheda/(?P<pk>[0-9]+)/mm/$', views.so_scheda_mm, name='scheda_mm'),
    url(r'^scheda/(?P<pk>[0-9]+)/mm/(?P<mm_pk>[0-9]+)/abbina/$', views.so_scheda_mm_abbina, name='scheda_mm_abbina'),
    url(r'^scheda/(?P<pk>[0-9]+)/mm/(?P<prenotazione>[0-9]+)/cancella/$', views.so_scheda_mm_cancella, name='scheda_mm_cancella'),

    # Turni
    url(r'^servizio/%s/turni/$' % pk, views.so_scheda_turni, name='servizio_turni'),
    url(r'^servizio/%s/turni/nuovo/$' % pk, views.so_scheda_turni_nuovo, name='servizio_turni_nuovo'),
    url(r'^servizio/%s/turni/(?P<pagina>[0-9]+)/$' % pk, views.so_scheda_turni, name='servizio_turni_pagina'),
    url(r'^servizio/%s/turni/(?P<turno_pk>[0-9]+)/partecipanti/$' % pk, views.so_scheda_turni_partecipanti, name='servizio_turni_partecipanti'),
    url(r'^servizio/%s/turni/(?P<turno_pk>[0-9]+)/ritirati/$' % pk, views.so_scheda_turni_ritirati, name='servizio_turni_ritirati'),
    url(r'^servizio/%s/turni/permalink/(?P<turno_pk>[0-9]+)/$' % pk, views.so_scheda_turni_permalink, name='servizio_turni_link_permanente'),
    url(r'^servizio/%s/turni/cancella/(?P<turno_pk>[0-9]+)/$' % pk, views.so_scheda_turni_turno_cancella, name='servizio_turni_cancella'),
    url(r'^servizio/%s/turni/modifica/$' % pk, views.so_scheda_turni_modifica, name='servizio_turni_modifica'),
    url(r'^servizio/%s/turni/modifica/(?P<pagina>[0-9]+)/$' % pk, views.so_scheda_turni_modifica, name='servizio_turni_modifica_pagina'),
    url(r'^servizio/%s/turni/modifica/permalink/(?P<turno_pk>[0-9]+)/$' % pk, views.so_scheda_turni_modifica_permalink, name='servizio_turni_modifica_link_permanente'),

    # Turno
    url(r'^turno/(?P<turno_pk>[0-9]+)/abbina/(?P<reperibilita_pk>[0-9]+)/$', views.so_turno_abbina_volontario, name='servizio_turno_abbina_volontario'),
    url(r'^turno/(?P<turno_pk>[0-9]+)/partecipazione/(?P<partecipazione_pk>[0-9]+)/cancella/$', views.so_scheda_partecipazione_cancella, name='servizio_partecipazione_cancella'),

    # Mezzi e materiali
    url(r'^mm/$', views.so_mezzi, name='mezzi'),
    url(r'^mm/%s/edit/$' % pk, views.so_mezzo_modifica, name='mezzo_modifica'),
    url(r'^mm/%s/delete/$' % pk, views.so_mezzo_cancella, name='mezzo_cancella'),
]
