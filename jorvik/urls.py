from .settings import MEDIA_ROOT, DEBUG
from django.contrib import admin
from django.conf.urls import include, url
from django.views.i18n import javascript_catalog
import django.contrib.auth.views

from oauth2_provider import views as oauth2_provider_views
from autenticazione.two_factor.urls import urlpatterns as tf_urls
from formazione import urls_aspirante as formazione_urls_aspirante
import anagrafica.viste
import articoli.viste
import autenticazione.viste
import base.viste, base.errori
import gestione_file.viste
import posta.viste
import social.viste
import ufficio_soci.viste


handler404 = base.errori.non_trovato

js_info_dict = {
    'packages': ('jorvik',),
}

urlpatterns = [
    url(r'^$', base.viste.index), # Home page

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

    # Informazioni
    url(r'^informazioni/$', base.viste.informazioni, name='informazioni'),
    url(r'^informazioni/statistiche/$', base.viste.informazioni_statistiche),
    url(r'^informazioni/aggiornamenti/$', base.viste.informazioni_aggiornamenti),
    url(r'^informazioni/sicurezza/$', base.viste.informazioni_sicurezza),
    url(r'^informazioni/condizioni/$', base.viste.informazioni_condizioni, name='informazioni_condizioni'),
    url(r'^informazioni/cookie/$', base.viste.informazioni_cookie, name='informazioni_cookie'),
    url(r'^informazioni/cookie/imposta/$', base.viste.imposta_cookie, name='imposta_cookie'),
    url(r'^informazioni/verifica-tesserino/$',
        ufficio_soci.viste.verifica_tesserino,
        name='informazioni_verifica_tesserino'),
    url(r'^informazioni/sedi/$', base.viste.informazioni_sedi),
    url(r'^informazioni/sedi/(?P<slug>.*)/$', base.viste.informazioni_sede),
    url(r'^informazioni/formazione/$', base.viste.formazione),
    url(r'^informazioni/browser-supportati/$', base.viste.browser_supportati, name='browser_supportati'),

    url(r'^profilo/(?P<pk>[0-9]+)/messaggio/$', anagrafica.viste.profilo_messaggio),
    url(r'^profilo/(?P<pk>[0-9]+)/turni/foglio/$', anagrafica.viste.profilo_turni_foglio),
    url(r'^profilo/(?P<pk>[0-9]+)/telefono/(?P<tel_pk>[0-9]+)/cancella/$', anagrafica.viste.profilo_telefono_cancella),
    url(r'^profilo/(?P<pk>[0-9]+)/documenti/(?P<documento_pk>[0-9]+)/cancella/$', anagrafica.viste.profilo_documenti_cancella),
    url(r'^profilo/(?P<pk>[0-9]+)/curriculum/(?P<tp_pk>[0-9]+)/cancella/$', anagrafica.viste.profilo_curriculum_cancella),
    url(r'^profilo/(?P<pk>[0-9]+)/sangue/(?P<donazione_pk>[0-9]+)/cancella/$', anagrafica.viste.profilo_sangue_cancella),
    url(r'^profilo/(?P<pk>[0-9]+)/(?P<sezione>.*)/$', anagrafica.viste.profilo, name='profilo'),
    url(r'^profilo/(?P<pk>[0-9]+)/$', anagrafica.viste.profilo),

    url(r'^autorizzazioni/$', base.viste.autorizzazioni, name='autorizzazioni-aperte'),
    url(r'^autorizzazioni/storico/$', base.viste.autorizzazioni_storico, name='autorizzazioni-storico'),
    url(r'^autorizzazioni/(?P<content_type_pk>[0-9]+)/$', base.viste.autorizzazioni, name='autorizzazioni-dettaglio'),
    url(r'^autorizzazioni/(?P<pk>[0-9]+)/concedi/$', base.viste.autorizzazione_concedi, name='autorizzazioni-concedi'),
    url(r'^autorizzazioni/(?P<pk>[0-9]+)/nega/$', base.viste.autorizzazione_nega, name='autorizzazioni-nega'),

    url(r'^posta/scrivi/', posta.viste.posta_scrivi, name='posta-scrivi'),
    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/(?P<messaggio_id>\d+)/', posta.viste.posta),
    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/', posta.viste.posta),
    url(r'^posta/(?P<direzione>[\w\-]+)/', posta.viste.posta),
    url(r'^posta/', posta.viste.posta_home),

    url(r'^articoli/$', articoli.viste.ListaArticoli.as_view(), name='lista_articoli'),
    url(r'^articoli/(?P<anno>\d{4})/$', articoli.viste.ListaArticoli.as_view(), name='lista_articoli-per-anno'),
    url(r'^articoli/(?P<anno>\d{4})/(?P<mese>\d{1,2})/$', articoli.viste.ListaArticoli.as_view(), name='lista_articoli-per-mese'),
    url(r'^articoli/(?P<articolo_slug>[\w\-]+)/$', articoli.viste.DettaglioArticolo.as_view(), name='dettaglio_articolo'),

    url(r'^documenti/$', gestione_file.viste.ListaDocumenti.as_view(), name='lista_documenti'),
    url(r'^documenti/(?P<cartella>[0-9\-]+)/$', gestione_file.viste.ListaDocumenti.as_view(), name='lista_documenti'),
    url(r'^documenti/scarica/(?P<pk>[0-9\-]+)/$', gestione_file.viste.serve_protected_file, name='scarica_file'),
    url(r'documenti/immagine/(?P<image_id>\d+)/$', gestione_file.viste.serve_image, name='scarica_immagine'),
    url(r'documenti/immagine/(?P<image_id>\d+)/(?P<thumb_options>\d+)/$', gestione_file.viste.serve_image, name='scarica_immagine'),
    url(r'documenti/immagine/(?P<image_id>\d+)/(?P<width>\d+)/(?P<height>\d+)/$', gestione_file.viste.serve_image, name='scarica_immagine'),

    url(r'^presidente/$', anagrafica.viste.presidente),
    url(r'^presidente/sedi/(?P<sede_pk>[0-9]+)/$', anagrafica.viste.presidente_sede),
    url(r'^presidente/sedi/(?P<sede_pk>[0-9]+)/delegati/(?P<delega>.*)/$', anagrafica.viste.presidente_sede_delegati),
    url(r'^presidente/checklist/(?P<sede_pk>[0-9]+)/$', anagrafica.viste.presidente_checklist),
    url(r'^presidente/checklist/(?P<sede_pk>[0-9]+)/(?P<tipo>.*)/(?P<oggetto_tipo>[0-9]+)/(?P<oggetto_id>[0-9]+)/',
        anagrafica.viste.presidente_checklist_delegati),

    # Applicazioni
    url(r'^centrale-operativa/', include('centrale_operativa.urls', namespace='centrale_operativa')),
    url(r'^autoparco/', include('veicoli.urls_autoparco', namespace='autoparco')),
    url(r'^attivita/', include('attivita.urls', namespace='attivita')),
    url(r'^veicoli/', include('veicoli.urls', namespace='veicoli')),
    url(r'^utente/', include('anagrafica.urls_utente', namespace='utente')),
    url(r'^us/', include('ufficio_soci.urls', namespace='ufficio_soci')),
    url(r'^cv/', include('curriculum.urls', namespace='cv')),

    # Formazione
    url(r'^aspirante/', include(formazione_urls_aspirante, namespace='aspirante')),
    url(r'^formazione/', include('formazione.urls', namespace='formazione')),
    url(r'^survey/', include('survey.urls', namespace='survey')),

    # Static pages
    url(r'^page/', include('static_page.urls', namespace='pages')),
    url(r'^supporto/$', base.viste.supporto, name='supporto_page'),

    url(r'^strumenti/delegati/$', anagrafica.viste.strumenti_delegati, name='strumenti_delegati'),
    url(r'^strumenti/delegati/(?P<delega_pk>[0-9]+)/termina/$', anagrafica.viste.strumenti_delegati_termina),
    url(r'^social/commenti/nuovo/', social.viste.commenti_nuovo),
    url(r'^social/commenti/cancella/(?P<pk>[0-9]+)/', social.viste.commenti_cancella),
    url(r'^media/(?P<path>.*)$', django.views.static.serve, {"document_root": MEDIA_ROOT}),
    url(r'^geo/localizzatore/imposta/$', base.viste.geo_localizzatore_imposta),
    url(r'^geo/localizzatore/$', base.viste.geo_localizzatore),
    url(r'^pdf/(?P<app_label>.*)/(?P<model>.*)/(?P<pk>[0-9]+)/$', base.viste.pdf),
    url(r'^token-sicuro/(?P<codice>.*)/$', base.viste.verifica_token),
    url(r'^password-dimenticata/$', base.viste.redirect_semplice, {"nuovo_url": "/recupera_password/"}),

    # Amministrazione
    url(r'^admin/import/volontari/$', anagrafica.viste.admin_import_volontari),
    url(r'^admin/import/presidenti/$', anagrafica.viste.admin_import_presidenti),
    url(r'^admin/pulisci/email/$', anagrafica.viste.admin_pulisci_email),
    url(r'^admin/statistiche/$', anagrafica.viste.admin_statistiche),
    url(r'^admin/statistiche/download/(?P<statistica>[0-9A-Za-z_\-]+)$', anagrafica.viste.admin_statistiche_download),
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
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^o/authorize/$', oauth2_provider_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^o/token/$', oauth2_provider_views.TokenView.as_view(), name="token"),
    url(r'^o/revoke_token/$', oauth2_provider_views.RevokeTokenView.as_view(), name="revoke-token"),
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),

    # REST api
    url(r'^api/', include('api.urls', namespace='api')),
]

if DEBUG:
    urlpatterns += [url(r'^api-auth/', include('rest_framework.urls')),]
