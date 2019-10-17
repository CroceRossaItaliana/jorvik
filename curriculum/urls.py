from django.conf.urls import url
from .views import cdf_titolo_json, cv_add_qualifica_cri

app_label = 'cv'
urlpatterns = [
    url(r'^cdf_titolo_json/$', cdf_titolo_json, name='cdf_titolo_json'),
    url(r'^qualifica/add/$', cv_add_qualifica_cri, name='add_qualifica_cri'),
]
