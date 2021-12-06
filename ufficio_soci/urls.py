from ufficio_soci import visite_mediche
from django.conf.urls import url
from . import viste

app_label = 'ufficio_soci'
urlpatterns = [
    url(r'^$', viste.us),
    url(r'^provvedimento/$', viste.us_provvedimento),
    url(r'^aggiungi/$', viste.us_aggiungi),
    url(r'^reclama/$', viste.us_reclama),
    url(r'^reclama/(?P<persona_pk>.*)/$', viste.us_reclama_persona),
    url(r'^estensione/$', viste.us_estensione),
    url(r'^estensione/(?P<pk>.*)/termina/$', viste.us_estensione_termina, name='us-termina-estensione'),
    url(r'^trasferimento/$', viste.us_trasferimento),
    url(r'^riserva/$', viste.us_riserva),
    url(r'^riserva/(?P<pk>.*)/termina/$', viste.us_riserva_termina),
    url(r'^dimissioni/(?P<pk>[0-9]+)/$', viste.us_dimissioni, name='us-dimissioni'),
    url(r'^dimissioni/sostenitore/(?P<pk>[0-9]+)/$', viste.us_chiudi_sostenitore, name='us-chiudi-sostenitore'),

    url(r'^elenchi/download/$', viste.us_elenchi_richiesti_download, name='elenchi_richiesti_download'),
    url(r'^elenchi/(?P<elenco_tipo>.*)/$', viste.us_elenchi),
    url(r'^quote/$', viste.us_quote),
    url(r'^quote/nuova/$', viste.us_quote_nuova, name='us_quote_nuova'),
    url(r'^ricevute/$', viste.us_ricevute),
    url(r'^ricevute/(?P<pk>[0-9]+)/annulla/$', viste.us_ricevute_annulla),
    url(r'^ricevute/nuova/$', viste.us_ricevute_nuova, name='us_ricevute_nuova'),

    url(r'^tesserini/$', viste.us_tesserini),
    url(r'^tesserini/da-richiedere/$', viste.us_tesserini_da_richiedere),
    url(r'^tesserini/senza-fototessera/$', viste.us_tesserini_senza_fototessera),
    url(r'^tesserini/richiesti/$', viste.us_tesserini_richiesti),
    url(r'^tesserini/rifiutati/$', viste.us_tesserini_rifiutati),
    url(r'^tesserini/richiedi/(?P<persona_pk>[0-9]+)/$', viste.us_tesserini_richiedi, name='us-tesserini-richiedi'),
    url(r'^tesserini/emissione/$', viste.us_tesserini_emissione),
    url(r'^tesserini/emissione/processa/$', viste.us_tesserini_emissione_processa),
    url(r'^tesserini/emissione/scarica/$', viste.us_tesserini_emissione_scarica),

    url(r'^elenco/(?P<elenco_id>.*)/(?P<pagina>[0-9]+)/$', viste.us_elenco, name='elenco_page'),
    url(r'^elenco/(?P<elenco_id>.*)/download/$', viste.us_elenco_download),
    url(r'^elenco/(?P<elenco_id>.*)/messaggio/$', viste.us_elenco_messaggio, name='us-elenco-messaggio'),
    url(r'^elenco/(?P<elenco_id>.*)/modulo/$', viste.us_elenco_modulo),
    url(r'^elenco/(?P<elenco_id>.*)/$', viste.us_elenco),

    url(r'^ricerca-visita-medica/', visite_mediche.ricerca_visite_mediche),
    url(r'^medici-comitato/', visite_mediche.lista_dottori),
    url(r'^prenota-visita-medica/', visite_mediche.prenota_visita),
]
