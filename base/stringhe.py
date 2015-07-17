"""
Funzioni per il trattamento delle stringhe.
"""

import string
import uuid
import os.path
from datetime import timedelta, datetime
from jorvik.settings import MEDIA_ROOT


def normalizza_nome(stringa):
    """
    Normalizza una stringa per l'uso come Nome o titolo.
    :param stringa: La stringa da normalizzare.
    :return: La stringa pronta come titolo.
    """
    return string.capwords(stringa)


def genera_uuid_casuale():
    """
    Genera una stringa univoca casuale usando la libreria uuid di python.
    :return: Qualcosa come 'A943C888-5F0B-40B9-BA80-50AB09C6D1D5'
    """
    return str(uuid.uuid4()).upper()


def generatore_nome_file(prefisso, forza_suffisso=None):
    """
    Ritorna un generatore di nome file casuale, sulla base di un prefisso.
    :param prefisso: Prefisso (es. "cartella/%Y/")
    :param forza_suffisso: Un suffisso da forzare (es. ".txt"), o suffisso originale se None
    :return: Una funzione che ogni volta chiamata ritorna qualcosa come
             {MEDIA_ROOT}/prefisso/C22AF346-8D6B-429B-B518-F85F7E69281F.suffisso
    """
    def generatore(instanza, originale):

        suffisso = forza_suffisso if forza_suffisso is not None \
            else os.path.splitext(originale)[1]

        return prefisso + genera_uuid_casuale() + suffisso

    return generatore  # Nota: ritorna una funzione!


def domani():
    """
    Ritorna la data di domani. Scorciatoia (generalmente usata per scadenza automatica Allegati).
    :return: datetime (solo date) a domani.
    """
    return datetime.now().date() + timedelta(1)
