from collections import OrderedDict

__author__ = 'alfioemanuele'

def unique(items):
    found = set([])
    keep = []

    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)

    return keep


def turni_raggruppa_giorno(qs_turni):
    """
    Da un elenco di turni (queryset), li raggruppa per giorno.
    NB: Questo effettua l'evaluation del queryset.
    :param qs_turni: I turni.
    :return:
        """
    giorni = unique([i.inizio.date() for i in qs_turni])
    risultato = OrderedDict([(d, []) for d in giorni])
    for d in giorni:
        for i in qs_turni:
            if i.inizio.date() == d:
                risultato[d].append(i)
    return risultato
