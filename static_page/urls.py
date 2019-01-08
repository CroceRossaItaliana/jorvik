from django.conf.urls import url
from .views import view_page


app_label = 'pages'
urlpatterns = [
    url(r'^(?P<slug>[\w\-]+)/$', view_page, name='page'),
]
