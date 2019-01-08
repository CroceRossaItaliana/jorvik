"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""
import django, django.views, django.views.static, django.contrib.auth.views
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done
from django.shortcuts import redirect
from django.views.i18n import javascript_catalog
from oauth2_provider import views as oauth2_provider_views

import anagrafica.viste
import articoli.viste
import attivita.viste
import autenticazione.viste
import base.viste, base.errori
import centrale_operativa.viste
import formazione.viste
import gestione_file.viste
import gruppi.viste
import posta.viste
import social.viste
import ufficio_soci.viste
import veicoli.viste
from anagrafica.forms import ModuloModificaPassword
from autenticazione.funzioni import pagina_privata, pagina_privata_no_cambio_firma
from jorvik.settings import MEDIA_ROOT, DEBUG

from autenticazione.two_factor.urls import urlpatterns as tf_urls


handler404 = base.errori.non_trovato

js_info_dict = {
    'packages': ('jorvik',),
}

urlpatterns = [

    # Home page!
    url(r'^$', base.viste.index),

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
    url(r'^informazioni/$', base.viste.informazioni),
    url(r'^informazioni/statistiche/$', base.viste.informazioni_statistiche),
    url(r'^informazioni/aggiornamenti/$', base.viste.informazioni_aggiornamenti),
    url(r'^informazioni/sicurezza/$', base.viste.informazioni_sicurezza),
    url(r'^informazioni/condizioni/$', base.viste.informazioni_condizioni, name='informazioni_condizioni'),
    url(r'^informazioni/cookie/$', base.viste.informazioni_cookie, name='informazioni_cookie'),
    url(r'^informazioni/cookie/imposta/$', base.viste.imposta_cookie, name='imposta_cookie'),
    url(r'^informazioni/verifica-tesserino/$', ufficio_soci.viste.verifica_tesserino),
    url(r'^informazioni/sedi/$', base.viste.informazioni_sedi),
    url(r'^informazioni/sedi/(?P<slug>.*)/$', base.viste.informazioni_sede),
    url(r'^informazioni/formazione/$', base.viste.formazione),
    url(r'^informazioni/browser-supportati/$', base.viste.browser_supportati, name='browser_supportati'),

    # Applicazioni
    url(r'^utente/$', anagrafica.viste.utente),
    url(r'^utente/anagrafica/$', anagrafica.viste.utente_anagrafica),
    url(r'^utente/estensione/$', anagrafica.viste.utente_estensione),
    url(r'^utente/trasferimento/$', anagrafica.viste.utente_trasferimento),
    url(r'^utente/fotografia/$', anagrafica.viste.utente_fotografia),
    url(r'^utente/fotografia/avatar/$', anagrafica.viste.utente_fotografia_avatar),
    url(r'^utente/fotografia/fototessera/$', anagrafica.viste.utente_fotografia_fototessera),
    url(r'^utente/documenti/$', anagrafica.viste.utente_documenti),
    url(r'^utente/documenti/zip/$', anagrafica.viste.utente_documenti_zip),
    url(r'^utente/documenti/cancella/(?P<pk>.*)/$', anagrafica.viste.utente_documenti_cancella),
    url(r'^utente/storico/$', anagrafica.viste.utente_storico),
    url(r'^utente/contatti/$', anagrafica.viste.utente_contatti),
    url(r'^utente/rubrica/referenti/$', anagrafica.viste.utente_rubrica_referenti),
    url(r'^utente/rubrica/volontari/$', anagrafica.viste.utente_rubrica_volontari),
    url(r'^utente/rubrica/(?P<rubrica>.*)/$', anagrafica.viste.rubrica_delegati),
    url(r'^utente/curriculum/$', anagrafica.viste.utente_curriculum),
    url(r'^utente/curriculum/(?P<pk>.*)/cancella/$', anagrafica.viste.utente_curriculum_cancella),
    url(r'^utente/curriculum/(?P<tipo>.*)/$', anagrafica.viste.utente_curriculum),
    url(r'^utente/riserva/$', anagrafica.viste.utente_riserva),
    url(r'^utente/riserva/(?P<pk>.*)/termina/$', anagrafica.viste.utente_riserva_termina),
    url(r'^utente/riserva/(?P<pk>.*)/ritira/$', anagrafica.viste.utente_riserva_ritira),
    url(r'^utente/contatti/cancella-numero/(?P<pk>.*)/$', anagrafica.viste.utente_contatti_cancella_numero),
    url(r'^utente/estensione/(?P<pk>.*)/estendi/$', anagrafica.viste.utente_estensione_estendi),
    url(r'^utente/estensione/(?P<pk>.*)/termina/$', anagrafica.viste.utente_estensione_termina),
    url(r'^utente/riserva/(?P<pk>.*)/termina/$', anagrafica.viste.utente_riserva_termina),
    url(r'^utente/trasferimento/(?P<pk>.*)/ritira/$', anagrafica.viste.utente_trasferimento_ritira),
    url(r'^utente/donazioni/profilo/$', anagrafica.viste.utente_donazioni_profilo),
    url(r'^utente/donazioni/sangue/(?P<pk>.*)/cancella/$', anagrafica.viste.utente_donazioni_sangue_cancella),
    url(r'^utente/donazioni/sangue/$', anagrafica.viste.utente_donazioni_sangue),
    url(r'^utente/privacy/$', anagrafica.viste.utente_privacy),
    url(r'^utente/cambia-password/?$', pagina_privata_no_cambio_firma(password_change), {
        "template_name": "anagrafica_utente_cambia_password.html",
        "password_change_form": ModuloModificaPassword,
        "post_change_redirect": "/utente/cambia-password/fatto/"
    }),
    url(r'^utente/cambia-password/fatto/$', pagina_privata_no_cambio_firma(password_change_done), {
        "template_name": "anagrafica_utente_cambia_password_fatto.html",
    }),

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
    url(r'^attivita/$', attivita.viste.attivita),
    url(r'^attivita/aree/$', attivita.viste.attivita_aree),
    url(r'^attivita/aree/(?P<sede_pk>[0-9\-]+)/$', attivita.viste.attivita_aree_sede),
    url(r'^attivita/aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/cancella/$', attivita.viste.attivita_aree_sede_area_cancella),
    url(r'^attivita/aree/(?P<sede_pk>[0-9\-]+)/(?P<area_pk>[0-9\-]+)/responsabili/$', attivita.viste.attivita_aree_sede_area_responsabili),
    url(r'^attivita/organizza/$', attivita.viste.attivita_organizza),
    url(r'^attivita/organizza/(?P<pk>[0-9\-]+)/referenti/$', attivita.viste.attivita_referenti, {"nuova": True}),
    url(r'^attivita/organizza/(?P<pk>[0-9\-]+)/fatto/$', attivita.viste.attivita_organizza_fatto),
    url(r'^attivita/statistiche/$', attivita.viste.attivita_statistiche),
    url(r'^attivita/gestisci/$', attivita.viste.attivita_gestisci, {"stato": "aperte"}),
    url(r'^attivita/gestisci/chiuse/$', attivita.viste.attivita_gestisci, {"stato": "chiuse"}),
    url(r'^attivita/calendario/$', attivita.viste.attivita_calendario),
    url(r'^attivita/calendario/(?P<inizio>[0-9\-]+)/(?P<fine>[0-9\-]+)/$', attivita.viste.attivita_calendario),
    url(r'^attivita/storico/$', attivita.viste.attivita_storico),
    url(r'^attivita/storico/excel/$', attivita.viste.attivita_storico_excel),
    url(r'^attivita/gruppo/$', gruppi.viste.attivita_gruppo),
    url(r'^attivita/gruppi/$', gruppi.viste.attivita_gruppi),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/$', gruppi.viste.attivita_gruppi_gruppo),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/iscriviti/$', gruppi.viste.attivita_gruppi_gruppo_iscriviti),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/espelli/(?P<persona_pk>[0-9]+)/$', gruppi.viste.attivita_gruppi_gruppo_espelli),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/abbandona/$', gruppi.viste.attivita_gruppi_gruppo_abbandona),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/elimina/$', gruppi.viste.attivita_gruppi_gruppo_elimina),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/elimina_conferma/$', gruppi.viste.attivita_gruppi_gruppo_elimina_conferma),
    url(r'^attivita/reperibilita/$', centrale_operativa.viste.attivita_reperibilita),
    url(r'^attivita/reperibilita/(?P<reperibilita_pk>[0-9]+)/cancella/$', centrale_operativa.viste.attivita_reperibilita_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/$', attivita.viste.attivita_scheda_informazioni),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/cancella-gruppo/$', attivita.viste.attivita_scheda_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/cancella/$', attivita.viste.attivita_scheda_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/mappa/$', attivita.viste.attivita_scheda_mappa),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/partecipanti/$', attivita.viste.attivita_scheda_partecipanti),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/$', attivita.viste.attivita_scheda_turni),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/(?P<pagina>[0-9]+)/$', attivita.viste.attivita_scheda_turni),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipa/$', attivita.viste.attivita_scheda_turni_partecipa),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/ritirati/$', attivita.viste.attivita_scheda_turni_ritirati),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/(?P<turno_pk>[0-9]+)/partecipanti/$', attivita.viste.attivita_scheda_turni_partecipanti),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/link-permanente/(?P<turno_pk>[0-9]+)/$', attivita.viste.attivita_scheda_turni_link_permanente),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/cancella/(?P<turno_pk>[0-9]+)/$', attivita.viste.attivita_scheda_turni_turno_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/modifica/$', attivita.viste.attivita_scheda_turni_modifica),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/nuovo/$', attivita.viste.attivita_scheda_turni_nuovo),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/partecipazione/(?P<partecipazione_pk>[0-9]+)/cancella/$', attivita.viste.attivita_scheda_partecipazione_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/modifica/(?P<pagina>[0-9]+)/$', attivita.viste.attivita_scheda_turni_modifica),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/turni/modifica/link-permanente/(?P<turno_pk>[0-9]+)/$', attivita.viste.attivita_scheda_turni_modifica_link_permanente),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/modifica/$', attivita.viste.attivita_scheda_informazioni_modifica),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/riapri/$', attivita.viste.attivita_riapri),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/referenti/$', attivita.viste.attivita_referenti),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/report/$', attivita.viste.attivita_scheda_report),

    url(r'^presidente/$', anagrafica.viste.presidente),
    url(r'^presidente/sedi/(?P<sede_pk>[0-9]+)/$', anagrafica.viste.presidente_sede),
    url(r'^presidente/sedi/(?P<sede_pk>[0-9]+)/delegati/(?P<delega>.*)/$', anagrafica.viste.presidente_sede_delegati),
    url(r'^presidente/checklist/(?P<sede_pk>[0-9]+)/$', anagrafica.viste.presidente_checklist),
    url(r'^presidente/checklist/(?P<sede_pk>[0-9]+)/(?P<tipo>.*)/(?P<oggetto_tipo>[0-9]+)/(?P<oggetto_id>[0-9]+)/',
        anagrafica.viste.presidente_checklist_delegati),

    url(r'^centrale-operativa/$', centrale_operativa.viste.co),
    url(r'^centrale-operativa/reperibilita/$', centrale_operativa.viste.co_reperibilita),
    url(r'^centrale-operativa/poteri/$', centrale_operativa.viste.co_poteri),
    url(r'^centrale-operativa/poteri/(?P<part_pk>[0-9]+)/$', centrale_operativa.viste.co_poteri_switch),
    url(r'^centrale-operativa/turni/$', centrale_operativa.viste.co_turni),
    url(r'^centrale-operativa/turni/(?P<partecipazione_pk>[0-9]+)/monta/$', centrale_operativa.viste.co_turni_monta),
    url(r'^centrale-operativa/turni/(?P<partecipazione_pk>[0-9]+)/smonta/$', centrale_operativa.viste.co_turni_smonta),

    url(r'^us/$', ufficio_soci.viste.us),
    url(r'^us/provvedimento/$', ufficio_soci.viste.us_provvedimento),
    url(r'^us/aggiungi/$', ufficio_soci.viste.us_aggiungi),
    url(r'^us/reclama/$', ufficio_soci.viste.us_reclama),
    url(r'^us/reclama/(?P<persona_pk>.*)/$', ufficio_soci.viste.us_reclama_persona),
    url(r'^us/estensione/$', ufficio_soci.viste.us_estensione),
    url(r'^us/estensione/(?P<pk>.*)/termina/$', ufficio_soci.viste.us_estensione_termina, name='us-termina-estensione'),
    url(r'^us/trasferimento/$', ufficio_soci.viste.us_trasferimento),
    url(r'^us/riserva/$', ufficio_soci.viste.us_riserva),
    url(r'^us/riserva/(?P<pk>.*)/termina/$', ufficio_soci.viste.us_riserva_termina),
    url(r'^us/dimissioni/(?P<pk>[0-9]+)/$', ufficio_soci.viste.us_dimissioni, name='us-dimissioni'),
    url(r'^us/dimissioni/sostenitore/(?P<pk>[0-9]+)/$', ufficio_soci.viste.us_chiudi_sostenitore, name='us-chiudi-sostenitore'),

    url(r'^us/elenchi/(?P<elenco_tipo>.*)/$', ufficio_soci.viste.us_elenchi),
    url(r'^us/quote/$', ufficio_soci.viste.us_quote),
    url(r'^us/quote/nuova/$', ufficio_soci.viste.us_quote_nuova, name='us_quote_nuova'),
    url(r'^us/ricevute/$', ufficio_soci.viste.us_ricevute),
    url(r'^us/ricevute/(?P<pk>[0-9]+)/annulla/$', ufficio_soci.viste.us_ricevute_annulla),
    url(r'^us/ricevute/nuova/$', ufficio_soci.viste.us_ricevute_nuova, name='us_ricevute_nuova'),

    url(r'^us/tesserini/$', ufficio_soci.viste.us_tesserini),
    url(r'^us/tesserini/da-richiedere/$', ufficio_soci.viste.us_tesserini_da_richiedere),
    url(r'^us/tesserini/senza-fototessera/$', ufficio_soci.viste.us_tesserini_senza_fototessera),
    url(r'^us/tesserini/richiesti/$', ufficio_soci.viste.us_tesserini_richiesti),
    url(r'^us/tesserini/rifiutati/$', ufficio_soci.viste.us_tesserini_rifiutati),
    url(r'^us/tesserini/richiedi/(?P<persona_pk>[0-9]+)/$', ufficio_soci.viste.us_tesserini_richiedi, name='us-tesserini-richiedi'),
    url(r'^us/tesserini/emissione/$', ufficio_soci.viste.us_tesserini_emissione),
    url(r'^us/tesserini/emissione/processa/$', ufficio_soci.viste.us_tesserini_emissione_processa),
    url(r'^us/tesserini/emissione/scarica/$', ufficio_soci.viste.us_tesserini_emissione_scarica),

    url(r'^us/elenco/(?P<elenco_id>.*)/(?P<pagina>[0-9]+)/$', ufficio_soci.viste.us_elenco),
    url(r'^us/elenco/(?P<elenco_id>.*)/download/$', ufficio_soci.viste.us_elenco_download),
    url(r'^us/elenco/(?P<elenco_id>.*)/messaggio/$', ufficio_soci.viste.us_elenco_messaggio, name='us-elenco-messaggio'),
    url(r'^us/elenco/(?P<elenco_id>.*)/modulo/$', ufficio_soci.viste.us_elenco_modulo),
    url(r'^us/elenco/(?P<elenco_id>.*)/$', ufficio_soci.viste.us_elenco),

    url(r'^veicoli/$', veicoli.viste.veicoli),
    url(r'^veicoli/elenco/$', veicoli.viste.veicoli_elenco),
    url(r'^veicoli/autoparchi/$', veicoli.viste.veicoli_autoparchi),
    url(r'^veicoli/autoparco/elenco/(?P<autoparco>.*)/$', veicoli.viste.veicoli_elenco_autoparco),
    url(r'^veicolo/(P<pk>.*)/$', veicoli.viste.veicoli_veicolo),
    url(r'^autoparco/(P<pk>.*)/$', veicoli.viste.veicoli_autoparco),
    url(r'^veicolo/nuovo/$', veicoli.viste.veicoli_veicolo_modifica_o_nuovo),
    url(r'^autoparco/nuovo/$', veicoli.viste.veicoli_autoparco_modifica_o_nuovo),
    url(r'^veicolo/modifica/(?P<pk>.*)/$', veicoli.viste.veicoli_veicolo_modifica_o_nuovo),
    url(r'^autoparco/modifica/(?P<pk>.*)/$', veicoli.viste.veicoli_autoparco_modifica_o_nuovo),
    url(r'^veicolo/manutenzioni/(?P<veicolo>.*)/$', veicoli.viste.veicoli_manutenzione),
    url(r'^veicolo/manutenzione/(?P<manutenzione>.*)/modifica/$', veicoli.viste.veicoli_modifica_manutenzione),
    url(r'^veicolo/rifornimento/(?P<rifornimento>.*)/modifica/$', veicoli.viste.veicoli_modifica_rifornimento),
    url(r'^veicolo/rifornimenti/(?P<veicolo>.*)/$', veicoli.viste.veicoli_rifornimento),
    url(r'^veicolo/fermi-tecnici/(?P<veicolo>.*)/$', veicoli.viste.veicoli_fermo_tecnico),
    url(r'^veicolo/termina/fermo-tecnico/(?P<fermo>.*)/$', veicoli.viste.veicoli_termina_fermo_tecnico),
    url(r'^veicolo/(?P<veicolo>.*)/collocazioni/$', veicoli.viste.veicoli_collocazioni),
    url(r'^veicolo/dettagli/(?P<veicolo>.*)/$', veicoli.viste.veicolo_dettagli),


    url(r'^aspirante/$', formazione.viste.aspirante_home),
    url(r'^aspirante/impostazioni/$', formazione.viste.aspirante_impostazioni),
    url(r'^aspirante/impostazioni/cancella/$', formazione.viste.aspirante_impostazioni_cancella),
    url(r'^aspirante/corsi-base/$', formazione.viste.aspirante_corsi_base),
    url(r'^aspirante/sedi/$', formazione.viste.aspirante_sedi),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/$', formazione.viste.aspirante_corso_base_informazioni),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/mappa/$', formazione.viste.aspirante_corso_base_mappa),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscritti/$', formazione.viste.aspirante_corso_base_iscritti),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscritti/aggiungi/$', formazione.viste.aspirante_corso_base_iscritti_aggiungi),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscritti/cancella/(?P<iscritto>[0-9]+)/$', formazione.viste.aspirante_corso_base_iscritti_cancella, name='formazione-iscritti-cancella'),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscriviti/$', formazione.viste.aspirante_corso_base_iscriviti),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/ritirati/$', formazione.viste.aspirante_corso_base_ritirati),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/report/$', formazione.viste.aspirante_corso_base_report),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/report/schede/$', formazione.viste.aspirante_corso_base_report_schede),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/firme/$', formazione.viste.aspirante_corso_base_firme),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/modifica/$', formazione.viste.aspirante_corso_base_modifica),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/attiva/$', formazione.viste.aspirante_corso_base_attiva),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/termina/$', formazione.viste.aspirante_corso_base_termina),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/lezioni/$', formazione.viste.aspirante_corso_base_lezioni),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/lezioni/(?P<lezione_pk>[0-9]+)/cancella/$', formazione.viste.aspirante_corso_base_lezioni_cancella),

    url(r'^formazione/$', formazione.viste.formazione),
    url(r'^formazione/corsi-base/elenco/$', formazione.viste.formazione_corsi_base_elenco),
    url(r'^formazione/corsi-base/domanda/$', formazione.viste.formazione_corsi_base_domanda),
    url(r'^formazione/corsi-base/nuovo/$', formazione.viste.formazione_corsi_base_nuovo),
    url(r'^formazione/corsi-base/(?P<pk>[0-9]+)/direttori/$', formazione.viste.formazione_corsi_base_direttori),
    url(r'^formazione/corsi-base/(?P<pk>[0-9]+)/fine/$', formazione.viste.formazione_corsi_base_fine),

    # Static pages
    url(r'^page/', include('static_page.urls', namespace='pages')),
    url(r'^supporto/$', base.viste.supporto),

    url(r'^geo/localizzatore/imposta/$', base.viste.geo_localizzatore_imposta),
    url(r'^geo/localizzatore/$', base.viste.geo_localizzatore),
    url(r'^strumenti/delegati/$', anagrafica.viste.strumenti_delegati),
    url(r'^strumenti/delegati/(?P<delega_pk>[0-9]+)/termina/$', anagrafica.viste.strumenti_delegati_termina),

    url(r'^social/commenti/nuovo/', social.viste.commenti_nuovo),
    url(r'^social/commenti/cancella/(?P<pk>[0-9]+)/', social.viste.commenti_cancella),

    url(r'^media/(?P<path>.*)$', django.views.static.serve, {"document_root": MEDIA_ROOT}),

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

    #Filer
    url(r'^filer/', include('filer.urls')),
    url(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

    # OAuth 2.0
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^o/authorize/$', oauth2_provider_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^o/token/$', oauth2_provider_views.TokenView.as_view(), name="token"),
    url(r'^o/revoke_token/$', oauth2_provider_views.RevokeTokenView.as_view(), name="revoke-token"),

    # REST api
    url(r'^api/', include('api.urls', namespace='api')),

]

if DEBUG:
    urlpatterns += [url(r'^api-auth/', include('rest_framework.urls')),]

