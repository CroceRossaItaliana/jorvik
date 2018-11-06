from django.conf.urls import url
from . import viste


app_label = 'aspirante'
urlpatterns = [
    url(r'^$', viste.aspirante_home),
    url(r'^impostazioni/$', viste.aspirante_impostazioni),
    url(r'^impostazioni/cancella/$', viste.aspirante_impostazioni_cancella),
    url(r'^corsi-base/$', viste.aspirante_corsi_base),
    url(r'^sedi/$', viste.aspirante_sedi),
    url(r'^corso-base/(?P<pk>[0-9]+)/$',
        viste.aspirante_corso_base_informazioni),
    url(r'^corso-base/(?P<pk>[0-9]+)/mappa/$',
        viste.aspirante_corso_base_mappa),
    url(r'^corso-base/(?P<pk>[0-9]+)/iscritti/$',
        viste.aspirante_corso_base_iscritti),
    url(r'^corso-base/(?P<pk>[0-9]+)/iscritti/aggiungi/$',
        viste.aspirante_corso_base_iscritti_aggiungi),
    url(r'^corso-base/(?P<pk>[0-9]+)/iscritti/cancella/(?P<iscritto>[0-9]+)/$',
        viste.aspirante_corso_base_iscritti_cancella,
        name='formazione_iscritti_cancella'),
    url(r'^corso-base/(?P<pk>[0-9]+)/iscriviti/$',
        viste.aspirante_corso_base_iscriviti),
    url(r'^corso-base/(?P<pk>[0-9]+)/ritirati/$',
        viste.aspirante_corso_base_ritirati),
    url(r'^corso-base/(?P<pk>[0-9]+)/report/$',
        viste.aspirante_corso_base_report),
    url(r'^corso-base/(?P<pk>[0-9]+)/report/schede/$',
        viste.aspirante_corso_base_report_schede),
    url(r'^corso-base/(?P<pk>[0-9]+)/firme/$',
        viste.aspirante_corso_base_firme),
    url(r'^corso-base/(?P<pk>[0-9]+)/modifica/$',
        viste.aspirante_corso_base_modifica),
    url(r'^corso-base/(?P<pk>[0-9]+)/attiva/$',
        viste.aspirante_corso_base_attiva),
    url(r'^corso-base/(?P<pk>[0-9]+)/termina/$',
        viste.aspirante_corso_base_termina),
    url(r'^corso-base/(?P<pk>[0-9]+)/lezioni/$',
        viste.aspirante_corso_base_lezioni),
    url(r'^corso-base/(?P<pk>[0-9]+)/lezioni/(?P<lezione_pk>[0-9]+)/cancella/$',
        viste.aspirante_corso_base_lezioni_cancella),
]
