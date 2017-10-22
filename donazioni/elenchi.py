from django.db.models import Q
from django.db.models.aggregates import Avg
from donazioni.models import Donazione, Donatore
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

    def risultati(self):
        qs = self.args[0]
        return qs.filter(fittizia=False)

    def filtra(self, queryset, termine):
        termini = termine.split(',')
        return queryset.filter(etichette__slug__in=termini)

    def template(self):
        return 'donazioni_elenchi_inc_campagne.html'


class ElencoEtichette(ElencoBase):

    def template(self):
        return 'donazioni_elenchi_inc_etichette.html'

    def filtra(self, queryset, termine):
        return queryset.filter(slug__icontains=termine)


class ElencoDonazioni(ElencoBase):

    def risultati(self):
        qs = self.args[0]
        # esclude le donazioni alle campagne fittizie (importo 0.00)
        return qs.exclude(campagna__fittizia=True)

    def template(self):
        return 'donazioni_elenchi_inc_donazioni.html'

    def ordina(self, qs):
        return qs.order_by('-data')

    def filtra(self, queryset, termine):
        termine = termine.lower()
        metodo_pagamento = Donazione.METODO_PAGAMENTO_REVERSE.get(termine)
        filtri = Q()
        if metodo_pagamento:
            filtri |= Q(metodo_pagamento=metodo_pagamento)
        filtri |= Q(Q(donatore__nome__icontains=termine) | Q(donatore__cognome__icontains=termine))
        filtri |= Q(campagna__nome__icontains=termine)
        return queryset.filter(filtri)


class ElencoDonatori(ElencoBase):

    def template(self):
        return 'donazioni_elenchi_inc_donatori.html'

    def risultati(self):
        qs = self.args[0]
        return qs.distinct('cognome', 'nome', 'email', 'codice_fiscale', 'partita_iva', 'ragione_sociale')

    def ordina(self, qs):
        return qs.order_by('cognome', 'nome', 'email', 'codice_fiscale', 'partita_iva', 'ragione_sociale')

    def filtra(self, queryset, termine='', scaglione_media=None):
        queryset = queryset.prefetch_related('donazioni')
        results = queryset
        if scaglione_media:
            # scaglione_media ha formato '0-50'
            tokens = scaglione_media.split('-')
            media_inf = tokens[0]
            media_sup = tokens[1]
            filtri = Q(media__gte=media_inf)
            if not media_sup == 'inf':
                filtri = filtri & Q(media__lte=media_sup)

            donatori_ids = queryset.values_list('id')
            queryset = Donatore.objects.filter(pk__in=donatori_ids).annotate(media=Avg('donazioni__importo')).filter(filtri)
            results = queryset.distinct()

        if termine:
            termine = termine.lower()
            donazioni_campagne_ids = Donazione.objects.filter(campagna__nome__icontains=termine).values_list('id')
            filtri = Q(Q(nome__icontains=termine) | Q(cognome__icontains=termine) |
                       Q(codice_fiscale__icontains=termine) | Q(email__icontains=termine) |
                       Q(donazioni__id__in=donazioni_campagne_ids))
            queryset = queryset.filter(filtri)
            results = queryset.distinct('cognome', 'nome', 'email', 'codice_fiscale', 'partita_iva', 'ragione_sociale')
        return results
