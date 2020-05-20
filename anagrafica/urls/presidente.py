from django.conf.urls import url
from anagrafica import viste


app_label = 'presidente'
pk = "(?P<sede_pk>[0-9]+)"
urlpatterns = [
    url(r'^$', viste.presidente),
    url(r'^sedi/%s/$' % pk, viste.presidente_sede, name='sedi_panoramico'),
    url(r'^sedi/%s/indirizzi/$' % pk, viste.presidente_sede_indirizzi, name="sede_indirizzi"),
    url(r'^sedi/%s/delegati/(?P<delega>.*)/$' % pk, viste.presidente_sede_delegati),
    url(r'^checklist/%s/$' % pk, viste.presidente_checklist),
    url(r'^checklist/%s/(?P<tipo>.*)/(?P<oggetto_tipo>[0-9]+)/(?P<oggetto_id>['r'0-9]+)/' % pk, viste.presidente_checklist_delegati),
]
