from django.conf.urls import url
from anagrafica import viste


app_label = 'profilo'
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/messaggio/$', viste.profilo_messaggio),
    url(r'^(?P<pk>[0-9]+)/turni/foglio/$', viste.profilo_turni_foglio),
    url(r'^(?P<pk>[0-9]+)/telefono/(?P<tel_pk>[0-9]+)/cancella/$', viste.profilo_telefono_cancella),
    url(r'^(?P<pk>[0-9]+)/documenti/(?P<documento_pk>[0-9]+)/cancella/$', viste.profilo_documenti_cancella),
    url(r'^(?P<pk>[0-9]+)/curriculum/(?P<tp_pk>[0-9]+)/cancella/$', viste.profilo_curriculum_cancella),
    url(r'^(?P<pk>[0-9]+)/sangue/(?P<donazione_pk>[0-9]+)/cancella/$', viste.profilo_sangue_cancella),
    url(r'^(?P<pk>[0-9]+)/(?P<sezione>.*)/$', viste.profilo, name='profilo'),
    url(r'^(?P<pk>[0-9]+)/$', viste.profilo, name="main"),
]
