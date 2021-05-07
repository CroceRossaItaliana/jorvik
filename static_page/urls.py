from django.conf.urls import url
from . import views


app_label = 'pages'
urlpatterns = [
    url(r'^monitoraggio/$', views.monitoraggio, name='monitoraggio'),
    url(r'^monitoraggio-trasparenza/$', views.monitoraggio_trasparenza, name='monitoraggio-trasparenza'),
    url(r'^monitora-trasparenza/$', views.monitora_trasparenza, name='monitora-trasparenza'),
    url(r'^monitora-autocontrollo/$', views.monitora_autocontrollo, name='monitora-autocontrollo'),
    url(r'^monitoraggio/actions/$', views.monitoraggio_actions, name='monitoraggio_actions'),
    url(r'^monitoraggio/nonsonounmersaglio/$', views.monitoraggio_nonsonounbersaglio, name='monitoraggio-nonsonounbersaglio'),
    url(r'^(?P<slug>[\w\-]+)/$', views.view_page, name='page')
]
