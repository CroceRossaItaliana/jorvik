from django.db.models import Q

from ufficio_soci.elenchi import Elenco


class ElencoBase(Elenco):
    """

    """

    def filtra(self, queryset, termine):
        raise NotImplementedError()

    def risultati(self):
        qs = self.args[0]
        return qs


class ElencoCampagne(ElencoBase):

    def filtra(self, queryset, termine):
        return queryset.filter(etichette__slug__in=[termine])

    def template(self):
        return 'donazioni_elenchi_inc_campagne.html'


class ElencoEtichette(ElencoBase):

    def template(self):
        return 'donazioni_elenchi_inc_etichette.html'

    def filtra(self, queryset, termine):
        return queryset.filter(slug__icontains=termine)


class ElencoDonazioni(ElencoBase):
    def template(self):
        return 'donazioni_elenchi_inc_donazioni.html'

    def filtra(self, queryset, termine):
        return queryset.filter(modalita__icontains=termine)


class ElencoDonatori(ElencoBase):
    def template(self):
        return 'donazioni_elenchi_inc_donatori.html'

    def filtra(self, queryset, termine):
        filtri = Q(Q(nome__icontains=termine) | Q(cognome__icontains=termine) |
                   Q(codice_fiscale__icontains=termine) | Q(email__icontains=termine)
                   )
        return queryset.filter(filtri)
