from django.db.models import Q

from ufficio_soci.elenchi import Elenco


class ElencoCampagne(Elenco):

    def risultati(self):
        qs_campagne = self.args[0]
        return qs_campagne

    def filtra(self, queryset, termine):
        return queryset.filter(etichette__slug__in=[termine])

    def template(self):
        return 'donazioni_elenchi_inc_campagne.html'


class ElencoEtichette(Elenco):

    def template(self):
        return 'donazioni_elenchi_inc_etichette.html'

    def risultati(self):
        qs_etichette = self.args[0]
        return qs_etichette

    def filtra(self, queryset, termine):
        return queryset.filter(slug__icontains=termine)


class ElencoDonazioni(Elenco):
    def template(self):
        return 'donazioni_elenchi_inc_donazioni.html'

    def risultati(self):
        qs_donazioni = self.args[0]
        return qs_donazioni

    def filtra(self, queryset, termine):
        return queryset.filter(modalita__icontains=termine)


class ElencoDonatori(Elenco):
    def template(self):
        return 'donazioni_elenchi_inc_donatori.html'

    def risultati(self):
        qs_donatori = self.args[0]
        return qs_donatori

    def filtra(self, queryset, termine):
        filtri = Q(Q(nome__icontains=termine) | Q(cognome__icontains=termine) |
                   Q(codice_fiscale__icontains=termine) | Q(email__icontains=termine)
                   )
        return queryset.filter(filtri)
