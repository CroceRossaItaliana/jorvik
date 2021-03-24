from django.conf.urls import url
from .. import viste as views


app_label = 'formazione'
urlpatterns = [
    url(r'^$', views.formazione, name='index'),
    url(r'^corsi-base/domanda/$', views.formazione_corsi_base_domanda, name='domanda'),
    url(r'^corsi-base/nuovo/$', views.formazione_corsi_base_nuovo, name='new_course'),
    url(r'^corsi-base/elenco/$', views.formazione_corsi_base_elenco, name='list_courses'),
    url(r'^corsi-base/(?P<pk>[0-9]+)/direttori/$', views.formazione_corsi_base_direttori, name='director'),
    url(r'^corsi-base/(?P<pk>[0-9]+)/fine/$', views.formazione_corsi_base_fine, name='end'),
    url(r'^albo-informatizzato/$', views.formazione_albo_informatizzato, name='albo_info'),
    url(r'^albo-informatizzato/titoli-corso-di-persona/$', views.formazione_albo_titoli_corso_full_list, name='albo_titoli_corso_full_list'),
    url(r'^observe/$', views.formazione_osserva_corsi, name='osserva_corsi'),
    url(r'^calendar/$', views.formazione_calendar, name='formazione_calendar'),
]
