from django.conf.urls import url
from anagrafica import viste


app_label = 'presidente'
urlpatterns = [
    url(r'^$', viste.presidente),
    url(r'^sedi/(?P<sede_pk>[0-9]+)/$', viste.presidente_sede),
    url(r'^sedi/(?P<sede_pk>[0-9]+)/delegati/(?P<delega>.*)/$', viste.presidente_sede_delegati),
    url(r'^checklist/(?P<sede_pk>[0-9]+)/$', viste.presidente_checklist),
    url(r'^checklist/(?P<sede_pk>[0-9]+)/(?P<tipo>.*)/(?P<oggetto_tipo>[0-9]+)/(?P<oggetto_id>[0-9]+)/', viste.presidente_checklist_delegati),
]
