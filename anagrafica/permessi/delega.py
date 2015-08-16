from anagrafica.permessi.funzioni import PERMESSI_FUNZIONI_DICT

__author__ = 'alfioemanuele'

def delega_permessi(delega):
    """
    Ottiene un elenco di permessi che scaturiscono dalla delega.
    :return: Una lista di permessi.
    """
    try:
        return PERMESSI_FUNZIONI_DICT[delega.tipo](delega.oggetto)
    except KeyError:
        return []