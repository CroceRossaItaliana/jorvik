import hashlib
import random
from collections import OrderedDict

from curriculum.areas import OBBIETTIVI_STRATEGICI
from curriculum.models import Titolo


def costruisci_titoli(context={}, qs=None, search_query='', key=''):
    for i in OBBIETTIVI_STRATEGICI:
        area_id, area_nome = i
        areas = qs.filter(area=i[0])

        context[key][area_nome] = OrderedDict()

        for k in Titolo.CDF_LIVELLI:
            level_id = k[0]
            levels = areas.filter(cdf_livello=level_id)
            context[key][area_nome]['level_%s' % level_id] = levels

        if search_query:
            # Fare pulizia dei settori che non hanno un risultato (solo nel caso di ricerca)
            settore_in_dict = context[key][area_nome]
            cleaned = OrderedDict((a,t) for a,t in dict(settore_in_dict).items() if t)
            if not len(cleaned):
                del context[key][area_nome]
            else:
                context[key][area_nome] = cleaned

    return context


def unique_signature(pk=None, creazione=None):
    # import sys
    signature = hashlib.md5(
        '{}{}'.format(
            pk,
            creazione.strftime("%m/%d/%Y, %H:%M:%S:%f")
        ).encode()
    )
    return signature.hexdigest()
