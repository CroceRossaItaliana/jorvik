from django.db.models import Q

from anagrafica.models import Persona
from formazione.models import InvitoCorsoBase, PartecipazioneCorsoBase
from ufficio_soci.elenchi import ElencoVistaAnagrafica


class ElencoPartecipantiCorsiBase(ElencoVistaAnagrafica):

    def template(self):
        return 'formazione_elenchi_inc_iscritti.html'

    def risultati(self):
        qs_corsi = self.args[0]
        return Persona.objects.filter(
            Q(PartecipazioneCorsoBase.con_esito_ok(corso__in=qs_corsi).via("partecipazioni_corsi")) |
            Q(inviti_corsi__in=InvitoCorsoBase.objects.filter(corso__in=qs_corsi))
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')
