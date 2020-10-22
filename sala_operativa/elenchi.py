from django.db.models import F

from anagrafica.models import Persona
from ufficio_soci.elenchi import ElencoVistaAnagrafica
from .models import PartecipazioneSO


class ElencoPartecipantiTurno(ElencoVistaAnagrafica):
    NAME = 'Partecipanti Turno'

    def risultati(self):
        qs_turni = self.args[0]
        return Persona.objects.filter(
            PartecipazioneSO.con_esito_ok(turno__in=qs_turni).via("partecipazioni_so")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

class ElencoPartecipantiAttivita(ElencoVistaAnagrafica):
    NAME = 'Partecipanti Attivita'

    def risultati(self):
        qs_attivita = self.args[0]
        return Persona.objects.filter(
            PartecipazioneSO.con_esito_ok(turno__attivita__in=qs_attivita).via("partecipazioni_so")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).annotate(
            partecipazioni__turno__nome=F('partecipazioni__turno__nome'),
            partecipazioni__turno__inizio=F('partecipazioni__turno__inizio'),
            partecipazioni__turno__fine=F('partecipazioni__turno__fine'),
        )  ## NO DISTINCT!

    def excel_colonne(self):
        return super().excel_colonne() + (
            ("Turno Nome", lambda p: p.partecipazioni__turno__nome),
            ("Turno Inizio", lambda p: p.partecipazioni__turno__inizio),
            ("Turno Fine", lambda p: p.partecipazioni__turno__fine,
        ))

    def template(self):
        return 'us_elenchi_inc_attivita.html'

    def excel_foglio(self, p):
        return "%s-%s" % (
            p.partecipazioni__turno__inizio.strftime("%Y-%m-%d"),
            p.partecipazioni__turno__nome,
        )

    def ordina(self, qs):
        return qs.order_by('partecipazioni__turno__inizio', 'nome', 'cognome', 'codice_fiscale')
