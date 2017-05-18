from django.db.models import Q

from anagrafica.models import Persona
from formazione.models import InvitoCorsoBase, PartecipazioneCorsoBase
from ufficio_soci.elenchi import ElencoVistaAnagrafica


class ElencoPartecipantiCorsiBase(ElencoVistaAnagrafica):

    def template(self):
        return 'formazione_elenchi_inc_iscritti.html'

    def excel_colonne(self):
        return super(ElencoPartecipantiCorsiBase, self).excel_colonne() + (
            ("Stato", lambda p: 'Iscritto' if not p.aspirante or self.args[0][0].pk not in p.aspirante.inviti_attivi else 'Invitato'),
        )

    def risultati(self):
        qs_corsi = self.args[0]
        return Persona.objects.filter(
            Q(PartecipazioneCorsoBase.con_esito_ok(corso__in=qs_corsi).via("partecipazioni_corsi")) |
            Q(InvitoCorsoBase.con_esito_ok(corso__in=qs_corsi).via("inviti_corsi")) |
            Q(InvitoCorsoBase.con_esito_pending(corso__in=qs_corsi).via("inviti_corsi"))
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')
