from django.contrib.contenttypes.models import ContentType

from ufficio_soci.elenchi import ElencoVistaAnagrafica, ElencoVolontariGiovani
from anagrafica.models import Persona, Delega, Sede


class ElencoDelegati(ElencoVistaAnagrafica):

    def risultati(self):
        qs_sedi = self.args[0]
        qs_deleghe = self.args[1]
        me = self.args[2]

        delegati = Persona.objects.filter(
            Delega.query_attuale(
                oggetto_tipo=ContentType.objects.get_for_model(Sede),
                oggetto_id__in=qs_sedi,
                tipo__in=qs_deleghe
            ).via("delega")
        ).exclude(pk=me.pk).order_by('nome', 'cognome', 'codice_fiscale')\
            .distinct('nome', 'cognome', 'codice_fiscale')
        return delegati


class ElencoGiovani(ElencoVolontariGiovani):

    def risultati(self):
        me = self.args[1]
        return super(ElencoGiovani, self).risultati().exclude(pk=me.pk)
