from django.conf.urls import url
from .views import view_page, monitoraggio


app_label = 'pages'
urlpatterns = [
    url(r'^monitoraggio-2019/$', monitoraggio, name='monitor-2019'),
    url(r'^(?P<slug>[\w\-]+)/$', view_page, name='page'),
]
