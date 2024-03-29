"""
Funzioni per il trattamento delle stringhe.
"""
import copy
from functools import partial

import string
import types
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
    return string.capwords(stringa.lower().replace("'", "' ")).replace("' ", "'")


def genera_uuid_casuale():
    """
    Genera una stringa univoca casuale usando la libreria uuid di python.
    :return: Qualcosa come 'A943C888-5F0B-40B9-BA80-50AB09C6D1D5'
    """
    return str(uuid.uuid4()).upper()


from django.utils.deconstruct import deconstructible


@deconstructible
class GeneratoreNomeFile():

    MAX_LENGTH = 80

    def __init__(self, prefisso, forza_suffisso=None):
        """
        :param prefisso: Prefisso (es. "cartella/%Y/")
        :param forza_suffisso: Un suffisso da forzare (es. ".txt"), o suffisso originale se None
        """
        self.prefisso = prefisso
        self.forza_suffisso = forza_suffisso

    def __call__(self, i, originale):
        """
        Ritorna un generatore di nome file casuale, sulla base di un prefisso.
        :return: Una funzione che ogni volta chiamata ritorna qualcosa come
                 {MEDIA_ROOT}/prefisso/C22AF346-8D6B-429B-B518-F85F7E69281F.suffisso
        """

        originale = originale.encode('ascii', 'ignore').decode()
        suffisso = self.forza_suffisso if self.forza_suffisso is not None \
            else os.path.splitext(originale)[1]

        nome_file = os.path.splitext(originale)[0]
        datetime_file = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
        lunghezza_tot = len(self.prefisso) + len(nome_file) + len(datetime_file) + len(suffisso)

        if lunghezza_tot > self.MAX_LENGTH:
            slice = self.MAX_LENGTH - (lunghezza_tot - len(nome_file))

            return self.prefisso + "{}{}".format(nome_file[:slice], datetime_file) + suffisso

        return self.prefisso + "{}{}".format(nome_file, datetime_file) + suffisso


def domani():
    """
    Ritorna la data di domani. Scorciatoia (generalmente usata per scadenza automatica Allegati).
    :return: datetime (solo date) a domani.
    """
    return datetime.now().date() + timedelta(1)
