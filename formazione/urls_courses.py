from django.conf.urls import url
from . import viste

""" 
La proposta è quella di spostare tutti gli url del modulo formazione 
sotto unico prefisso: "courses/<pk>/action?params"
"""


app_label = 'courses'
pk = "(?P<pk>[0-9]+)"

urlpatterns = [
    url(r'^%s/questionnaire/send-to-participants/$' % pk,
        viste.course_send_questionnaire_to_participants,
        name='send_questionnaire_to_participants'),
    url(r'^%s/relazione-direttore/$' % pk,
        viste.corso_compila_relazione_direttore,
        name='compila_relazione_direttore'),
    url(r'^%s/file/$' % pk,
        viste.course_materiale_didattico_download,
        name='materiale_didattico_download'),
]
