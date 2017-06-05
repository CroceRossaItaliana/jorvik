"""
Utilita' varie.


Include il codice di ConceptQ
https://github.com/yourcelf/django-conceptq

"""
import copy
import operator
from functools import reduce

from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.db.models import Q, F
import urllib

from django.utils import timezone
from lxml import html
from django.db import models
from base.stringhe import normalizza_nome

from jorvik import settings

def is_list(x):
    """
    Controlla se un oggetto e' una lista o meno.
    :param x: L'oggetto da controllare.
    :return: True se x e' una lista, False altrimenti.
    """
    return isinstance(x, list)


def iterabile(oggetto):
    try:
        iterator = iter(oggetto)
    except TypeError:
        return False
    else:
        return True


def prefix(accessor, q):
    """
    Take a Q object, and prefix its keys so that it can be used from a related
    model.  Also prefixes F expressions.
    Example:
    >>> from django.db.models import Q
    >>> prefix("mailing", Q(sent__isnull=True))
    u"(AND: ("mailing__sent__isnull", True))"
    """
    q = copy.deepcopy(q)
    return _prefix_q(accessor, q, None, None)

def _prefix_q(accessor, q, parent, index):
    if isinstance(q, Q):
        for i, child in enumerate(q.children):
            _prefix_q(accessor, child, q.children, i)
    elif parent is not None and index is not None:
        (k, v) = q
        if isinstance(v, F):
            v = F("__".join(a for a in (accessor, v.name) if a))
        parent[index] = ("__".join(a for a in (accessor, k) if a), v)
    return q

def concept(method):
    """
    This is a decorator for methods on Django manager classes.  It expects the
    method to return a single Q object; however, once decorated, straight calls
    of the method will wrap the Q in a filter to return a queryset.

    -- Modified to work both on Managers and Models.
    """
    def func(self, *args, **kwargs):
        q = method(self, *args, **kwargs)
        if hasattr(self, 'objects'):
            qs = self.objects.filter(q)
        else:
            qs = self.filter(q)
        qs.q = q
        qs.via = lambda accessor: prefix(accessor, q)
        return qs
    return func

from autoslug.settings import slugify as default_slugify
def sede_slugify(value):
    """
    Utilizzato come funzione per la slugifyazione delle sedi
    """
    parole_vietate = ('comitato', 'di', 'della', 'del', 'in', 'provinciale',
                      'locale', 'territoriale', 'regionale', 'nazionale',)
    value = value.replace('d\'', '').replace('D\'', '')
    stringa = default_slugify(value)
    for parola in parole_vietate:
        stringa = stringa.replace(parola + str("-"), "")
    return stringa


def filtra_queryset(queryset, termini_ricerca, campi_ricerca=[]):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if termini_ricerca and termini_ricerca:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in campi_ricerca]
            for bit in termini_ricerca.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))

        return queryset


def remove_none(obj):
    """
    Rimuove riorsivamente gli elementi None da una lista, tupla o insieme.
    :param obj:
    :return:
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((remove_none(k), remove_none(v)) for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj


def testo_euro(numero, simbolo_html=False):
    euro = round(float(numero), 2)
    simbolo = "&euro;" if simbolo_html else "€"
    return ("%s%s %s" % (intcomma(int(euro)), ("%0.2f" % euro)[-3:], simbolo)).replace('.', ',')


def get_drive_file(file):
    req = urllib.request.Request("https://docs.google.com/feeds/download/documents/export/Export?id=%s&exportFormat=html" %(file,))
    str = urllib.request.urlopen(req).read().decode('UTF-8')
    doc = html.document_fromstring(str)
    head = doc.xpath('//head')[0]
    head.tag = 'div'
    body = doc.xpath('//body')[0]
    body.tag = 'div'
    str = html.tostring(head)+html.tostring(body)
    return str


class UpperCaseCharField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        try:
            value = value.upper()
        except (ValueError, TypeError, AttributeError):
            pass
        return value


class TitleCharField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(TitleCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        try:
            value = normalizza_nome(value)
            setattr(model_instance, self.attname, value)
            return value
        except (ValueError, TypeError, AttributeError):
            return super(TitleCharField, self).pre_save(model_instance, add)


def ean13_carattere_di_controllo(first12digits):
    charList = [char for char in first12digits]
    ean13 = [1,3]
    total = 0
    for order, char in enumerate(charList):
        total += int(char) * ean13[order % 2]
    checkDigit = 10 - total % 10
    if (checkDigit == 10):
        return 0
    return checkDigit


def poco_fa():
    """
    Un secondo fa. Utile per terminare o iniziare le appartenenze.
    """
    return timezone.now() - timedelta(minutes=1)


def oggi():
    return poco_fa().date()


def questo_anno():
    return poco_fa().year


def timedelta_ore(td):
    g, h = td.days, td.seconds/3600
    return h + 24*g


def rimuovi_scelte(scelte=[], tupla=()):
    """
    Rimuove una lista di scelte da una tupla choices
     e ritorna la nuova tupla.
    """
    nuova_tupla = ()
    for chiave, valore in tupla:
        if not chiave in scelte:
            nuova_tupla += ((chiave, valore),)
    return nuova_tupla


def calcola_scadenza(scadenza=None):
    oggi = timezone.now()
    if scadenza:
        giorni = scadenza
    else:
        giorni = settings.SCADENZA_AUTORIZZAZIONE_AUTOMATICA
    if type(giorni) == int:
        giorni = timedelta(days=giorni)
    scadenza = oggi + giorni
    return scadenza
