from django.conf.urls import url
from . import viste

""" 
La proposta è quella di spostare tutti gli url del modulo formazione 
sotto unico prefisso: "courses/<pk>/action?params"
"""


app_label = 'courses'
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/questionnaire/send-to-participants/$',
        viste.course_send_questionnaire_to_participants,
        name='send_questionnaire_to_participants'),
]
