from datetime import date
from anagrafica.permessi.costanti import permesso_minimo, LETTURA
from anagrafica.permessi.espansioni import ESPANDI_PERMESSI, espandi_persona
from django.utils import timezone

from anagrafica.permessi.funzioni import permessi_persona

__author__ = 'alfioemanuele'


def persona_oggetti_permesso(persona, permesso, al_giorno=None):
    """
    Dato un permesso, ritorna un queryset agli oggetti che sono coperti direttamente
    dal permesso. Es.: GESTINE_SOCI -> Elenco dei Comitati in cui si ha gestione dei soci.
    :param permesso: Permesso singolo.
    :param al_giorno: Data di verifica.
    :return: QuerySet. Se permesso non valido, QuerySet vuoto o None (EmptyQuerySet).
    """
    if not permesso:
        return True

    qs = None

    # Permessi derivanti dalla persona
    for (p, o) in permessi_persona(persona):
        if p == permesso:
            if qs is None:
                qs = o
            else:
                qs = qs | o

    # Permessi derivanti dalle deleghe
    deleghe_attuali = persona.deleghe_attuali(al_giorno=al_giorno, solo_attive=True)

    for d in deleghe_attuali:
        for (p, o) in d.permessi():
            if p == permesso:
                if qs is None:
                    qs = o
                else:
                    qs = qs | o

    if qs is not None:
        return qs.distinct()
    else:
        return qs


def persona_permessi(persona, oggetto, al_giorno=None,
                     solo_deleghe_attive=True):
    """
    Ritorna il livello di permessi che si ha su un qualunque oggetto.

    Se non e' necessario conoscere il livello, ma si vuole controllare se si hanno
     abbastanza permessi, la funzione booleanea Persona.permessi_almeno(oggetto, minimo)
     dovrebbe essere preferita, in quanto ottimizzata (ie. smette di ricercare una volta
     superato il livello minimo di permesso che si sta cercando).

    :param oggetto: Oggetto qualunque.
    :param al_giorno:  Data di verifica.
    :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
    :return: Intero. NESSUNO...COMPLETO
    """

    permessi = []

    # Permessi derivanti dalla persona
    for (permesso, queryset) in permessi_persona(persona):
        permessi += ESPANDI_PERMESSI[permesso][queryset]

    # Per ogni delega attuale, aggiungi i permessi
    for d in persona.deleghe_attuali(al_giorno=al_giorno, solo_attive=solo_deleghe_attive):
        ## [(permesso, oggetto), ...] = PERMESSI_DELEGA[d.tipo](d.oggetto)  # ie. ((
        for (permesso, queryset) in d.permessi():
            permessi += ESPANDI_PERMESSI[permesso](queryset)

    massimo = permesso_minimo(oggetto.__class__)  # ie. NESSUNO
    for (permesso, queryset) in permessi:  # p: (PERMESSO, queryset)

        # OPT: Inutile cercare qui, non migliorerebbe permesso
        if permesso <= massimo:
            continue

        # Non cerco tra oggetti di tipo diverso!
        if queryset.model != oggetto.__class__:
            continue

        # Okay, quindi ora controllo se l'oggetto e' in questo queryset
        if queryset.filter(pk=oggetto.pk).exists():
            massimo = permesso

    return massimo


def persona_permessi_almeno(persona, oggetto, minimo=LETTURA, al_giorno=None,
                            solo_deleghe_attive=True):
    """
    Controlla se ho i permessi minimi richiesti specificati su un dato oggetto.

    :param oggetto: Oggetto qualunque.
    :param minimo: Oggetto qualunque.
    :param al_giorno:  Data di verifica.
    :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
    :return: True se permessi >= minimo, False altrimenti
    """


    if permesso_minimo(oggetto.__class__) >= minimo:
        return True

    #if persona.admin:
    #    return True

    permessi = []

    # I permessi base di ogni persona
    permessi += espandi_persona(persona=persona, al_giorno=al_giorno)

    # Permessi derivanti dalla persona
    for (permesso, queryset) in permessi_persona(persona):
        permessi += ESPANDI_PERMESSI[permesso](queryset)

    # Per ogni delega attuale, aggiungi i permessi
    for d in persona.deleghe_attuali(al_giorno=al_giorno, solo_attive=solo_deleghe_attive):
        ## [(permesso, oggetto), ...] = PERMESSI_DELEGA[d.tipo](d.oggetto)  # ie. ((
        for (permesso, queryset) in d.permessi(solo_deleghe_attive=solo_deleghe_attive):
            permessi += ESPANDI_PERMESSI[permesso](queryset)

    for (permesso, queryset) in permessi:  # p: (PERMESSO, queryset)
        # Non cerco tra oggetti di tipo diverso!
        if queryset.model != oggetto.__class__:
            continue
        # Okay, quindi ora controllo se l'oggetto e' in questo queryset
        if queryset.filter(pk=oggetto.pk).exists():
            if permesso >= minimo:
                return True

    return False


def persona_ha_permesso(persona, permesso, al_giorno=None,
                        solo_deleghe_attive=True):
    """
    Dato un permesso, ritorna true se il permesso e' posseduto.
    :param permesso: Permesso singolo.
    :param al_giorno: Data di verifica.
    :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
    :return: True se il permesso e' posseduto. False altrimenti.
    """
    if not permesso:
        return True

    # Permessi derivanti dalla persona
    for (p, o) in permessi_persona(persona):
        if p == permesso and o.exists():
            return True

    # Permessi derivanti dalle deleghe
    for d in persona.deleghe_attuali(al_giorno=al_giorno, solo_attive=solo_deleghe_attive):
        for (p, o) in d.permessi():
            if p == permesso:
                return True

    return False


def persona_ha_permessi(persona, *permessi, solo_deleghe_attive=True):
    """
    Dato un elenco di permessi, ritorna True se tutti i permessi sono posseduti.
    :param permessi: Elenco di permessi.
    :param al_giorno: Data di verifica.
    :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
    :return: True se tutti i permessi sono posseduti. False altrimenti.
    """
    if persona.admin:
        return True
    for p in permessi:
        if isinstance(p, (list, tuple)):  # Tupla
            if not persona.ha_permessi(*p, solo_deleghe_attive=solo_deleghe_attive):
                return False
        else:  # Singolo permesso
            if not persona.ha_permesso(p, solo_deleghe_attive=solo_deleghe_attive):
                return False
    return True