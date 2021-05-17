from django.conf.urls import url
from . import views


app_label = 'pages'
urlpatterns = [
    url(r'^monitoraggio/$', views.monitoraggio, name='monitoraggio'),
    url(r'^monitoraggio-trasparenza/$', views.monitoraggio_trasparenza, name='monitoraggio-trasparenza'),
    url(r'^monitoraggio-fabb-info-territoriale/$', views.monitoraggio_fabb_info_territoriale, name='monitoraggio-fabb-info-territoriale'),
    url(r'^monitoraggio-fabb-info-ragionale/$', views.monitoraggio_fabb_info_regionale, name='monitoraggio-fabb-info-regionale'),
    url(r'^monitora-trasparenza/$', views.monitora_trasparenza, name='monitora-trasparenza'),
    url(r'^monitora-autocontrollo/$', views.monitora_autocontrollo, name='monitora-autocontrollo'),
    url(r'^monitora-fabb-info-territoriale/$', views.monitora_fabb_info_territoriale, name='monitora-fabb-info-territoriale'),
    url(r'^monitora-fabb-info-regionale/$', views.monitora_fabb_info_regionale, name='monitora-fabb-info-regionale'),
    url(r'^monitoraggio/actions/$', views.monitoraggio_actions, name='monitoraggio_actions'),
    url(r'^monitoraggio/nonsonounmersaglio/$', views.monitoraggio_nonsonounbersaglio, name='monitoraggio-nonsonounbersaglio'),
    url(r'^(?P<slug>[\w\-]+)/$', views.view_page, name='page')
]
