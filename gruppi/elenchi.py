from anagrafica.models import Persona
from anagrafica.models import Appartenenza as App
from ufficio_soci.elenchi import ElencoVistaAnagrafica
from .models import Gruppo, Appartenenza


class ElencoMembriGruppo(ElencoVistaAnagrafica):

    def risultati(self):
        qs_sedi = self.args[0]
        gruppo = self.args[1]

        return Persona.objects.filter(
            Appartenenza.query_attuale().via("appartenenze_gruppi"),
            App.query_attuale(sede__in=qs_sedi).via("appartenenze"),
            appartenenze_gruppi__gruppo=gruppo
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def template(self):
        return 'us_elenchi_inc_gruppo.html'

