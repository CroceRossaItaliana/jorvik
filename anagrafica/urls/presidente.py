from django.conf.urls import url
from anagrafica import viste


app_label = 'presidente'
pk = "(?P<sede_pk>[0-9]+)"
urlpatterns = [
    url(r'^$', viste.presidente),

    # Locazione
    url(r'^sedi/%s/$' % pk, viste.presidente_sede, name='sedi_panoramico'),
    url(r'^sedi/%s/indirizzi/$' % pk, viste.presidente_sede_indirizzi, name="sede_indirizzi"),

    # Nominativi
    url(r'^sedi/%s/nominativi/(?P<nominativo_pk>[0-9]+)/modifica/$' % pk,
        viste.sede_nominativo_modifica,
        name="sede_nominativo_modifica"),
    url(r'^sedi/%s/nominativi/(?P<nominativo_pk>[0-9]+)/termina/$' % pk,
        viste.sede_nominativo_termina,
        name="sede_nominativo_termina"),
    url(r'^sedi/%s/so/(?P<sede_operativa_pk>[0-9]+)/$' % pk,
        viste.presidente_sede_operativa_indirizzo,
        name="sede_operativa"),
    url(r'^sedi/%s/nominativi/$' % pk, viste.presidente_sede_nominativi,
        name="sede_nominativi"),

    # Delegati
    url(r'^sedi/%s/delegati/(?P<delega>.*)/$' % pk, viste.presidente_sede_delegati),
    url(r'^checklist/%s/$' % pk, viste.presidente_checklist),
    url(r'^checklist/%s/(?P<tipo>.*)/(?P<oggetto_tipo>[0-9]+)/(?P<oggetto_id>['r'0-9]+)/' % pk, viste.presidente_checklist_delegati),
    url(r'inscrizione_evento', viste.inscrizione_evento, name='inscrizione_evento'),

    # Operatori di sala
    url(r'operatori/(?P<pk>[0-9]+)/termina', viste.operatori_sale_termina, name="operatori_sale_termina"),
    url(r'operatori/', viste.operatori_sale, name="operatori_sale"),

]
