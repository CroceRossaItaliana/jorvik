from .settings import MEDIA_ROOT, DEBUG
from django.contrib import admin
from django.conf.urls import include, url
from django.views.i18n import javascript_catalog
import django.contrib.auth.views

from oauth2_provider import views as oauth2_provider_views
from autenticazione.two_factor.urls import urlpatterns as tf_urls
import anagrafica.viste
import autenticazione.viste
import base.viste, base.errori
import social.viste


handler404 = base.errori.non_trovato

js_info_dict = {
    'packages': ('jorvik',),
}

urlpatterns = [
    url(r'^$', base.viste.index),  # Home page

    # Moduli di registrazione
    url(r'^registrati/(?P<tipo>\w+)/conferma/$', anagrafica.viste.registrati_conferma),
    url(r'^registrati/(?P<tipo>\w+)/$', anagrafica.viste.registrati),
    url(r'^registrati/(?P<tipo>\w+)/(?P<step>\w+)/$', anagrafica.viste.registrati),

    # Modalita' manutenzione
    url(r'^manutenzione/$', base.viste.manutenzione),

    # Pagina di errore
    url(r'^errore/404/$', base.errori.non_trovato),
    url(r'^errore/orfano/$', base.errori.orfano),
    url(r'^errore/permessi/$', base.errori.permessi, name='errore-permessi'),

    # Login e logout
    # url(r'^login/$', base.errori.vista_ci_siamo_quasi),
    url(r'^', include(tf_urls, 'two_factor')),   # 2FA
    url(r'^scaduta/$', base.viste.sessione_scaduta),
    url(r'^logout/$', autenticazione.viste.logout, {'template_name': 'base_logout.html'}, name='logout'),
    url(r'^', include('django.contrib.auth.urls')),

    # Modulo di recupero password
    url(r'^recupera_password/$', base.viste.recupera_password, name='recupera_password'),
    url(r'^reimposta_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        base.viste.recupera_password_conferma, name='recupera_password_conferma'),
    url(r'^recupera_password_completo/$', base.viste.recupero_password_completo, name='recupero_password_completo'),

    # Applicazioni
    url(r'^centrale-operativa/', include('centrale_operativa.urls', namespace='centrale_operativa')),
    url(r'^articoli/', include('articoli.urls', namespace='articoli')),
    url(r'^autorizzazioni/', include('base.urls.autorizzazioni', namespace='autorizzazioni')),
    url(r'^documenti/', include('gestione_file.urls', namespace='documenti')),
    url(r'^informazioni/', include('base.urls.informazioni', namespace='informazioni')),
    url(r'^autoparco/', include('veicoli.urls_autoparco', namespace='autoparco')),
    url(r'^attivita/', include('attivita.urls', namespace='attivita')),
    url(r'^veicoli/', include('veicoli.urls', namespace='veicoli')),
    url(r'^utente/', include('anagrafica.urls.utente', namespace='utente')),
    url(r'^profilo/', include('anagrafica.urls.profilo', namespace='profilo')),
    url(r'^presidente/', include('anagrafica.urls.presidente', namespace='presidente')),
    url(r'^posta/', include('posta.urls', namespace='posta')),
    url(r'^us/', include('ufficio_soci.urls', namespace='ufficio_soci')),
    url(r'^cv/', include('curriculum.urls', namespace='cv')),
    url(r'^so/', include('sala_operativa.urls', namespace='so')),

    # Formazione
    url(r'^formazione/', include('formazione.urls.formazione', namespace='formazione')),
    url(r'^aspirante/', include('formazione.urls.aspirante', namespace='aspirante')),
    url(r'^courses/', include('formazione.urls.courses', namespace='courses')),
    url(r'^survey/', include('survey.urls', namespace='survey')),

    # Static pages
    url(r'^page/', include('static_page.urls', namespace='pages')),
    url(r'^supporto/$', base.viste.supporto, name='supporto_page'),

    url(r'^strumenti/delegati/$', anagrafica.viste.strumenti_delegati, name='strumenti_delegati'),
    url(r'^strumenti/delegati/(?P<delega_pk>[0-9]+)/termina/$', anagrafica.viste.strumenti_delegati_termina),
    url(r'^social/commenti/nuovo/', social.viste.commenti_nuovo),
    url(r'^social/commenti/cancella/(?P<pk>[0-9]+)/', social.viste.commenti_cancella),
    url(r'^media/(?P<path>.*)$', django.views.static.serve, {"document_root": MEDIA_ROOT}),
    url(r'^geo/localizzatore/imposta/$', base.viste.geo_localizzatore_imposta, name='geo_localizzatore_imposta'),
    url(r'^geo/localizzatore/$', base.viste.geo_localizzatore, name='geo_localizzatore'),
    url(r'^pdf/(?P<app_label>.*)/(?P<model>.*)/(?P<pk>[0-9]+)/$', base.viste.pdf),
    url(r'^token-sicuro/(?P<codice>.*)/$', base.viste.verifica_token),
    url(r'^password-dimenticata/$', base.viste.redirect_semplice, {"nuovo_url": "/recupera_password/"}),

    # Amministrazione
    url(r'^admin/import/volontari/$', anagrafica.viste.admin_import_volontari),
    url(r'^admin/import/presidenti/$', anagrafica.viste.admin_import_presidenti),
    url(r'^admin/pulisci/email/$', anagrafica.viste.admin_pulisci_email),
    url(r'^admin/statistiche/$', anagrafica.viste.admin_statistiche),
    url(r'^admin/report_federazione/$', anagrafica.viste.admin_report_federazione),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', include('loginas.urls')),   # Login come utente

    # Autocompletamento
    url(r'^autocomplete/', include('autocomplete_light.urls')),

    # Filer
    url(r'^filer/', include('filer.urls')),
    url(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

    # OAuth 2.0
    #url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^o/authorize/$', oauth2_provider_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^o/token/$', oauth2_provider_views.TokenView.as_view(), name="token"),
    url(r'^o/revoke_token/$', oauth2_provider_views.RevokeTokenView.as_view(), name="revoke-token"),
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),

    # REST api
    url(r'^api/', include('api.urls', namespace='api')),
]

if DEBUG:
    urlpatterns += [url(r'^api-auth/', include('rest_framework.urls')),]
