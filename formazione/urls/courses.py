from django.conf.urls import url
from .. import viste as views


""" 
La proposta è quella di spostare tutti gli url del modulo formazione 
sotto unico prefisso: "courses/<pk>/action?params"
"""


app_label = 'courses'
pk = "(?P<pk>[0-9]+)"

urlpatterns = [
    url(r'^%s/questionnaire/send-to-participants/$' % pk,
        views.course_send_questionnaire_to_participants,
        name='send_questionnaire_to_participants'),
    url(r'^%s/relazione-direttore/$' % pk,
        views.corso_compila_relazione_direttore,
        name='compila_relazione_direttore'),
    url(r'^%s/file/$' % pk,
        views.course_materiale_didattico_download,
        name='materiale_didattico_download'),
    url(r'^%s/commissione-esame/$' % pk,
        views.course_commissione_esame,
        name='commissione_esame'),
    url(r'^%s/lezione/(?P<lezione_pk>[0-9]+)/save/$' % pk,
        views.course_lezione_save,
        name='lezione_save'),
    url(r'^%s/lezione/dividi/(?P<lezione_pk>[0-9]+)/$' % pk,
        views.course_lezione_dividi,
        name='lezione_dividi'),
    url(r'catalog/$', views.catalogo_corsi, name='catalog')
]
