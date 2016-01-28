from anagrafica.models import Persona
from formazione.models import PartecipazioneCorsoBase
from ufficio_soci.elenchi import ElencoVistaAnagrafica


class ElencoPartecipantiCorsiBase(ElencoVistaAnagrafica):

    def risultati(self):
        qs_corsi = self.args[0]
        return Persona.objects.filter(
            PartecipazioneCorsoBase.con_esito_ok(corso__in=qs_corsi).via("partecipazioni_corsi")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')
