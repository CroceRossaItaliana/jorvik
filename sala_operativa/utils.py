from collections import OrderedDict

from anagrafica.permessi.costanti import GESTIONE_SO_SEDE, GESTIONE_SERVIZI


def unique(items):
    found = set([])
    keep = list()

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


def visibilita_menu_top(persona):
    if persona.volontario and not persona.ha_aspirante:
        if persona.ha_permesso(GESTIONE_SO_SEDE):
            return True
        elif persona.ha_permesso(GESTIONE_SERVIZI):
            return True
        else:
            # todo:
            return True
    return False
