"""
Utilita' varie.


Include il codice di ConceptQ
https://github.com/yourcelf/django-conceptq

"""
import copy
from django.db.models import Q, F


def is_list(x):
    """
    Controlla se un oggetto e' una lista o meno.
    :param x: L'oggetto da controllare.
    :return: True se x e' una lista, False altrimenti.
    """
    return isinstance(x, list)


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