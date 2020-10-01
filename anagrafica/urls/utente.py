from django.conf.urls import url
from django.contrib.auth.views import password_change, password_change_done

from autenticazione.funzioni import pagina_privata, pagina_privata_no_cambio_firma
from anagrafica.forms import ModuloModificaPassword

from anagrafica import viste as views


app_label = 'utente'
urlpatterns = [
    url(r'^$', views.utente, name='main'),
    url(r'^anagrafica/$', views.utente_anagrafica, name='anagrafica'),
    url(r'^estensione/$', views.utente_estensione, name='estensione'),
    url(r'^trasferimento/$', views.utente_trasferimento, name='trasferimento'),
    url(r'^riserva/$', views.utente_riserva, name='riserva'),
    url(r'^fotografia/$', views.utente_fotografia, name='foto'),
    url(r'^fotografia/avatar/$', views.utente_fotografia_avatar, name='avatar'),
    url(r'^fotografia/fototessera/$', views.utente_fotografia_fototessera, name='fototessera'),
    url(r'^documenti/$', views.utente_documenti, name='documenti'),
    url(r'^documenti/zip/$', views.utente_documenti_zip, name='documenti_zip'),
    url(r'^documenti/cancella/(?P<pk>.*)/$', views.utente_documenti_cancella, name='remove_document'),
    url(r'^storico/$', views.utente_storico, name='storico'),
    url(r'^contatti/$', views.utente_contatti, name='contatti'),
    url(r'^rubrica/referenti/$', views.utente_rubrica_referenti),
    url(r'^rubrica/volontari/$', views.utente_rubrica_volontari),
    url(r'^rubrica/servizio-civile/$', views.utente_rubrica_servizio_civile),
    url(r'^rubrica/(?P<rubrica>.*)/$', views.rubrica_delegati, name='rubrica'),
    url(r'^curriculum/$', views.utente_curriculum),
    url(r'^curriculum/(?P<pk>.*)/cancella/$', views.utente_curriculum_cancella),
    url(r'^curriculum/(?P<tipo>.*)/$', views.utente_curriculum, name='cv_tipo'),
    url(r'^riserva/(?P<pk>.*)/termina/$', views.utente_riserva_termina),
    url(r'^riserva/(?P<pk>.*)/ritira/$', views.utente_riserva_ritira),
    url(r'^contatti/cancella-numero/(?P<pk>.*)/$', views.utente_contatti_cancella_numero),
    url(r'^estensione/(?P<pk>.*)/estendi/$', views.utente_estensione_estendi),
    url(r'^estensione/(?P<pk>.*)/termina/$', views.utente_estensione_termina),
    url(r'^riserva/(?P<pk>.*)/termina/$', views.utente_riserva_termina),
    url(r'^trasferimento/(?P<pk>.*)/ritira/$', views.utente_trasferimento_ritira),
    url(r'^donazioni/profilo/$', views.utente_donazioni_profilo),
    url(r'^donazioni/sangue/(?P<pk>.*)/cancella/$', views.utente_donazioni_sangue_cancella),
    url(r'^donazioni/sangue/$', views.utente_donazioni_sangue),
    url(r'^privacy/$', views.utente_privacy, name='privacy'),
    url(r'^cambia-password/?$', pagina_privata_no_cambio_firma(password_change), {
        "template_name": "anagrafica_utente_cambia_password.html",
        "password_change_form": ModuloModificaPassword,
        "post_change_redirect": "/utente/cambia-password/fatto/"
    }, name='change_password'),
    url(r'^cambia-password/fatto/$', pagina_privata_no_cambio_firma(password_change_done), {
        "template_name": "anagrafica_utente_cambia_password_fatto.html",
    }),
]
