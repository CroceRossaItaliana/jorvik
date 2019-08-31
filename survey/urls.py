from django.conf.urls import url
from .views import course_survey, course_survey_download_results


app_label = 'survey'
urlpatterns = [
    url(r'^course/(?P<pk>[0-9]+)/$', course_survey, name='course'),
    url(r'^course/(?P<pk>[0-9]+)/download/$', course_survey_download_results,
        name='course_download_results'),
]
