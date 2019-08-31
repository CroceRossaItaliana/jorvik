from django.conf.urls import url

from .viste import posta, posta_home, posta_scrivi


app_label = 'posta'
urlpatterns = [
    url(r'^scrivi/', posta_scrivi, name='scrivi'),
    url(r'^(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/(?P<messaggio_id>\d+)/', posta),
    url(r'^(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/', posta),
    url(r'^(?P<direzione>[\w\-]+)/', posta),
    url(r'^', posta_home),
]
