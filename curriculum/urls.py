from django.conf.urls import url
from . import views

app_label = 'cv'
urlpatterns = [
    url(r'^cdf_titolo_json/$', views.cdf_titolo_json, name='cdf_titolo_json'),
    url(r'^qualifica/add/$', views.cv_add_qualifica_cri, name='add_qualifica_cri'),
    url(r'^qualifica/notifica_comitato_regionale_dati_errati/(?P<pk>[0-9]+)/',
        views.cv_qualifica_errata_notifica_comitato_regionale,
        name='notifica_comitato_regionale_dati_errati'),
]
