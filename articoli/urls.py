from django.conf.urls import url
from . import viste


app_label = 'articoli'
urlpatterns = [
    url(r'^$', viste.ListaArticoli.as_view(), name='lista'),
    url(r'^(?P<anno>\d{4})/$', viste.ListaArticoli.as_view(), name='per_anno'),
    url(r'^(?P<anno>\d{4})/(?P<mese>\d{1,2})/$', viste.ListaArticoli.as_view(), name='per_mese'),
    url(r'^(?P<articolo_slug>[\w\-]+)/$', viste.DettaglioArticolo.as_view(), name='dettaglio'),
]
