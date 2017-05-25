from anagrafica.permessi.funzioni import PERMESSI_FUNZIONI_DICT
from anagrafica.permessi.incarichi import ESPANSIONE_DELEGHE

__author__ = 'alfioemanuele'


def delega_permessi(delega):
    """
    Ottiene un elenco di permessi che scaturiscono dalla delega.
    :return: Una lista di permessi.
    """
    if delega.stato != delega.ATTIVA:
        return []  # Nessun permesso dalle deleghe sospese.

    try:
        return PERMESSI_FUNZIONI_DICT[delega.tipo](delega.oggetto)
    except KeyError:
        return []


def delega_incarichi(delega):
    """
    Ottiene un elenco di incarichi che scaturiscono dalla delega
    :param delega:
    :return: Una lista di tuple (incarico, qs_oggetto)
    """
    if delega.tipo in ESPANSIONE_DELEGHE \
            and delega.oggetto is not None \
            and delega.stato == delega.ATTIVA:
        return ESPANSIONE_DELEGHE[delega.tipo](delega.oggetto.queryset_modello())
    return []
