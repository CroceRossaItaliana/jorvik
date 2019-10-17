from django.conf.urls import url
from .views import cdf_titolo_json

app_label = 'cv'
urlpatterns = [
    url(r'^cdf_titolo_json/$', cdf_titolo_json, name='cdf_titolo_json'),
]
