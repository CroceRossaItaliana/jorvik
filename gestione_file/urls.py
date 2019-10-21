from django.conf.urls import url

from . import viste


app_label = 'documenti'
urlpatterns = [
    url(r'^$', viste.ListaDocumenti.as_view(), name='lista_documenti'),
    url(r'^(?P<cartella>[0-9\-]+)/$', viste.ListaDocumenti.as_view(), name='lista_documenti'),
    url(r'^scarica/(?P<pk>[0-9\-]+)/$', viste.serve_protected_file, name='scarica_file'),
    url(r'immagine/(?P<image_id>\d+)/$', viste.serve_image, name='scarica_immagine'),
    url(r'immagine/(?P<image_id>\d+)/(?P<thumb_options>\d+)/$', viste.serve_image, name='scarica_immagine'),
    url(r'immagine/(?P<image_id>\d+)/(?P<width>\d+)/(?P<height>\d+)/$', viste.serve_image, name='scarica_immagine'),
]
