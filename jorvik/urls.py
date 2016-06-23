"""
Questo modulo contiene la configurazione per il routing degli URL.

(c)2015 Croce Rossa Italiana
"""
import django, django.views, django.views.static, django.contrib.auth.views
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done
from django.shortcuts import redirect

import anagrafica.viste
import attivita.viste
import base.viste, base.errori
import centrale_operativa.viste
import formazione.viste
import gruppi.viste
import posta.viste
import social.viste
import ufficio_soci.viste
import veicoli.viste
from anagrafica.forms import ModuloModificaPassword
from autenticazione.funzioni import pagina_privata, pagina_privata_no_cambio_firma
from jorvik.settings import MEDIA_ROOT

handler404 = base.errori.non_trovato

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
    url(r'^errore/permessi/$', base.errori.permessi),

    # Login e logout
    # url(r'^login/$', base.errori.vista_ci_siamo_quasi),
    url(r'^login/$', django.contrib.auth.views.login, {'template_name': 'base_login.html'}),
    url(r'^logout/$', django.contrib.auth.views.logout, {'template_name': 'base_logout.html'}),
    url('^', include('django.contrib.auth.urls')),

    # Modulo di recupero password
    url(r'^recupera_password/$', base.viste.recupera_password, name='recupera_password'),
    url(r'^reimposta_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        base.viste.recupera_password_conferma, name='recupera_password_conferma'),
    url(r'^recupera_password_completo/$', base.viste.recupero_password_completo, name='recupero_password_completo'),

    # Informazioni
    url(r'^informazioni/$', base.viste.informazioni),
    url(r'^informazioni/aggiornamenti/$', base.viste.informazioni_aggiornamenti),
    url(r'^informazioni/sicurezza/$', base.viste.informazioni_sicurezza),
    url(r'^informazioni/condizioni/$', base.viste.informazioni_condizioni),
    url(r'^informazioni/verifica-tesserino/$', ufficio_soci.viste.verifica_tesserino),
    url(r'^informazioni/sedi/$', base.viste.informazioni_sedi),
    url(r'^informazioni/sedi/(?P<slug>.*)/$', base.viste.informazioni_sede),
    url(r'^informazioni/formazione/$', base.viste.formazione),

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
    url(r'^utente/rubrica/presidenti/$', anagrafica.viste.delegato_rubrica_presidenti),
    url(r'^utente/rubrica/delegati_us/$', anagrafica.viste.delegato_rubrica_delegati_us),
    url(r'^utente/rubrica/delegati_us_unita/$', anagrafica.viste.delegato_rubrica_delegati_us_unita_territoriale),
    url(r'^utente/rubrica/delegati_area/$', anagrafica.viste.delegato_rubrica_delegati_area),
    url(r'^utente/rubrica/delegati_obiettivo_1/$', anagrafica.viste.delegato_rubrica_delegati_obiettivo_1),
    url(r'^utente/rubrica/delegati_obiettivo_2/$', anagrafica.viste.delegato_rubrica_delegati_obiettivo_2),
    url(r'^utente/rubrica/delegati_obiettivo_3/$', anagrafica.viste.delegato_rubrica_delegati_obiettivo_3),
    url(r'^utente/rubrica/delegati_obiettivo_4/$', anagrafica.viste.delegato_rubrica_delegati_obiettivo_4),
    url(r'^utente/rubrica/delegati_obiettivo_6/$', anagrafica.viste.delegato_rubrica_delegati_obiettivo_6),
    url(r'^utente/rubrica/responsabili_area/$', anagrafica.viste.delegato_rubrica_responsabili_area),
    url(r'^utente/rubrica/referenti_attivita/$', anagrafica.viste.delegato_rubrica_referenti_attivita),
    url(r'^utente/rubrica/referenti_gruppi/$', anagrafica.viste.delegato_rubrica_referenti_gruppo),
    url(r'^utente/rubrica/centrali_operative/$', anagrafica.viste.delegato_rubrica_delegati_centrale_operativa),
    url(r'^utente/rubrica/responsabili_formazione/$', anagrafica.viste.delegato_rubrica_responsabili_formazione),
    url(r'^utente/rubrica/direttori_corsi/$', anagrafica.viste.delegato_rubrica_direttori_corso),
    url(r'^utente/rubrica/responsabili_autoparco/$', anagrafica.viste.delegato_rubrica_responsabili_autoparco),
    url(r'^utente/rubrica/giovani/$', anagrafica.viste.giovane_rubrica_giovani),
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
    url(r'^profilo/(?P<pk>[0-9]+)/(?P<sezione>.*)/$', anagrafica.viste.profilo),
    url(r'^profilo/(?P<pk>[0-9]+)/$', anagrafica.viste.profilo),

    url(r'^autorizzazioni/$', base.viste.autorizzazioni),
    url(r'^autorizzazioni/storico/$', base.viste.autorizzazioni_storico),
    url(r'^autorizzazioni/(?P<content_type_pk>[0-9]+)/$', base.viste.autorizzazioni),
    url(r'^autorizzazioni/(?P<pk>[0-9]+)/concedi/$', base.viste.autorizzazione_concedi),
    url(r'^autorizzazioni/(?P<pk>[0-9]+)/nega/$', base.viste.autorizzazione_nega),

    url(r'^posta/scrivi/', posta.viste.posta_scrivi),
    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/(?P<messaggio_id>\d+)/', posta.viste.posta),
    url(r'^posta/(?P<direzione>[\w\-]+)/(?P<pagina>\d+)/', posta.viste.posta),
    url(r'^posta/(?P<direzione>[\w\-]+)/', posta.viste.posta),
    url(r'^posta/', posta.viste.posta_home),

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
    url(r'^attivita/gruppi/$', gruppi.viste.attivita_gruppi),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/$', gruppi.viste.attivita_gruppi_gruppo),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/iscriviti/$', gruppi.viste.attivita_gruppi_gruppo_iscriviti),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/espelli/(?P<persona_pk>[0-9]+)/$', gruppi.viste.attivita_gruppi_gruppo_espelli),
    url(r'^attivita/gruppi/(?P<pk>[0-9]+)/abbandona/$', gruppi.viste.attivita_gruppi_gruppo_abbandona),
    url(r'^attivita/reperibilita/$', centrale_operativa.viste.attivita_reperibilita),
    url(r'^attivita/reperibilita/(?P<reperibilita_pk>[0-9]+)/cancella/$', centrale_operativa.viste.attivita_reperibilita_cancella),
    url(r'^attivita/scheda/(?P<pk>[0-9]+)/$', attivita.viste.attivita_scheda_informazioni),
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
    url(r'^us/estensione/(?P<pk>.*)/termina/$', ufficio_soci.viste.us_estensione_termina),
    url(r'^us/trasferimento/$', ufficio_soci.viste.us_trasferimento),
    url(r'^us/riserva/$', ufficio_soci.viste.us_riserva),
    url(r'^us/riserva/(?P<pk>.*)/termina/$', ufficio_soci.viste.us_riserva_termina),
    url(r'^us/dimissioni/(?P<pk>[0-9]+)/$', ufficio_soci.viste.us_dimissioni),

    url(r'^us/elenchi/(?P<elenco_tipo>.*)/$', ufficio_soci.viste.us_elenchi),
    url(r'^us/quote/$', ufficio_soci.viste.us_quote),
    url(r'^us/quote/nuova/$', ufficio_soci.viste.us_quote_nuova),
    url(r'^us/ricevute/$', ufficio_soci.viste.us_ricevute),
    url(r'^us/ricevute/(?P<pk>[0-9]+)/annulla/$', ufficio_soci.viste.us_ricevute_annulla),
    url(r'^us/ricevute/nuova/$', ufficio_soci.viste.us_ricevute_nuova),

    url(r'^us/tesserini/$', ufficio_soci.viste.us_tesserini),
    url(r'^us/tesserini/da-richiedere/$', ufficio_soci.viste.us_tesserini_da_richiedere),
    url(r'^us/tesserini/senza-fototessera/$', ufficio_soci.viste.us_tesserini_senza_fototessera),
    url(r'^us/tesserini/richiesti/$', ufficio_soci.viste.us_tesserini_richiesti),
    url(r'^us/tesserini/richiedi/(?P<persona_pk>[0-9]+)/$', ufficio_soci.viste.us_tesserini_richiedi),
    url(r'^us/tesserini/emissione/$', ufficio_soci.viste.us_tesserini_emissione),
    url(r'^us/tesserini/emissione/processa/$', ufficio_soci.viste.us_tesserini_emissione_processa),
    url(r'^us/tesserini/emissione/scarica/$', ufficio_soci.viste.us_tesserini_emissione_scarica),

    url(r'^us/elenco/(?P<elenco_id>.*)/(?P<pagina>[0-9]+)/$', ufficio_soci.viste.us_elenco),
    url(r'^us/elenco/(?P<elenco_id>.*)/download/$', ufficio_soci.viste.us_elenco_download),
    url(r'^us/elenco/(?P<elenco_id>.*)/messaggio/$', ufficio_soci.viste.us_elenco_messaggio),
    url(r'^us/elenco/(?P<elenco_id>.*)/modulo/$', ufficio_soci.viste.us_elenco_modulo),
    url(r'^us/elenco/(?P<elenco_id>.*)/$', ufficio_soci.viste.us_elenco),

    url(r'^veicoli/$', veicoli.viste.veicoli),
    url(r'^veicoli/elenco/$', veicoli.viste.veicoli_elenco),
    url(r'^veicoli/autoparchi/$', veicoli.viste.veicoli_autoparchi),
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

    url(r'^aspirante/$', formazione.viste.aspirante_home),
    url(r'^aspirante/impostazioni/$', formazione.viste.aspirante_impostazioni),
    url(r'^aspirante/impostazioni/cancella/$', formazione.viste.aspirante_impostazioni_cancella),
    url(r'^aspirante/corsi-base/$', formazione.viste.aspirante_corsi_base),
    url(r'^aspirante/sedi/$', formazione.viste.aspirante_sedi),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/$', formazione.viste.aspirante_corso_base_informazioni),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/mappa/$', formazione.viste.aspirante_corso_base_mappa),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscritti/$', formazione.viste.aspirante_corso_base_iscritti),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscritti/aggiungi/$', formazione.viste.aspirante_corso_base_iscritti_aggiungi),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/iscriviti/$', formazione.viste.aspirante_corso_base_iscriviti),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/ritirati/$', formazione.viste.aspirante_corso_base_ritirati),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/report/$', formazione.viste.aspirante_corso_base_report),
    url(r'^aspirante/corso-base/(?P<pk>[0-9]+)/report/schede/$', formazione.viste.aspirante_corso_base_report_schede),
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

    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include('loginas.urls')),   # Login come utente



    # Autocompletamento
    url(r'^autocomplete/', include('autocomplete_light.urls')),

    # OAuth 2.0
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
