from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from anagrafica.models import Persona, Delega, Sede
from anagrafica.permessi.costanti import DELEGHE_OGGETTI_DICT
from ufficio_soci.elenchi import ElencoVistaAnagrafica


class ElencoDelegati(ElencoVistaAnagrafica):
    deleghe = None

    def template(self):
        return 'anagrafica_elenchi_delegati.html'

    def risultati(self):
        qs_sedi = self.args[0]
        self.deleghe = self.kwargs['deleghe']
        me = self.kwargs['me_id']
        delegati = Persona.objects.none()
        for delega in self.deleghe:
            tipo = None
            oggetti = None
            if delega in DELEGHE_OGGETTI_DICT and DELEGHE_OGGETTI_DICT[delega][1] != 'Sede':
                try:
                    model = apps.get_model(DELEGHE_OGGETTI_DICT[delega][0], DELEGHE_OGGETTI_DICT[delega][1])
                    tipo = ContentType.objects.get_for_model(model)
                    oggetti = model.objects.filter(**{DELEGHE_OGGETTI_DICT[delega][2]: qs_sedi})
                except Exception as e:
                    pass
            if not tipo:
                tipo = ContentType.objects.get_for_model(Sede)
                oggetti = qs_sedi
            if oggetti:
                delegati |= Persona.objects.filter(
                    Delega.query_attuale(
                        oggetto_tipo=tipo,
                        oggetto_id__in=oggetti,
                        tipo=delega
                    ).via('delega')
                ).exclude(pk=me)
        return delegati.order_by('nome', 'cognome', 'codice_fiscale')\
            .distinct('nome', 'cognome', 'codice_fiscale')
