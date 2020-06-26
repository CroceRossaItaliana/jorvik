from django.conf.urls import url
from . import views as so_views


app_label = 'so'
urlpatterns = [
    url(r'^$', so_views.sala_operativa_index, name='index'),

    # Reperibilita
    url(r'^r/$', so_views.sala_operativa_reperibilita, name='reperibilita'),
    url(r'^r/backup/$', so_views.sala_operativa_reperibilita_backup, name='reperibilita_backup'),
    url(r'^r/(?P<r_pk>[0-9]+)/delete/$', so_views.sala_operativa_reperibilita_cancella, name='reperibilita_cancella'),
    url(r'^r/(?P<r_pk>[0-9]+)/edit/$', so_views.sala_operativa_reperibilita_edit, name='reperibilita_modifica'),

    # Servizi
    url(r'^s/$', so_views.sala_operativa_servizi, name='servizi'),
    url(r'^s/add/$', so_views.sala_operativa_servizi_aggiungi, name='servizio_aggiungi'),
    url(r'^s/(?P<pk>[0-9]+)/$', so_views.sala_operativa_servizio_dettagli, name='servizio_dettagli'),
    url(r'^s/(?P<pk>[0-9]+)/delete/$', so_views.sala_operativa_servizio_cancella, name='servizio_cancella'),
    url(r'^s/(?P<pk>[0-9]+)/add/vo/(?P<reperibilita_pk>[0-9]+)/$', so_views.sala_operativa_servizio_abbina_vo, name='servizio_add_vo'),
    url(r'^s/(?P<pk>[0-9]+)/remove/vo/(?P<reperibilita_pk>[0-9]+)/$', so_views.sala_operativa_servizio_rimuovi_vo, name='togli_dal_servizio'),

    # Turni
    url(r'^t/$', so_views.sala_operativa_turni, name='turni'),

    # Poteri
    url(r'^p/$', so_views.sala_operativa_poteri, name='poteri'),
]
