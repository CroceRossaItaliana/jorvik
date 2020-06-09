from django.conf.urls import url
from . import views


app_label = 'so'
urlpatterns = [
    url(r'^$', views.sala_operativa_index, name='index'),
    url(r'^reperibilita/$', views.sala_operativa_reperibilita, name='reperibilita'),
    url(r'^turni/$', views.sala_operativa_turni, name='turni'),
    url(r'^poteri/$', views.sala_operativa_poteri, name='poteri'),
]
