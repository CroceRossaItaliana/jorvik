import stdnum
import re

from datetime import datetime, date
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from stdnum.it import codicefiscale


def _valida_codice_fiscale(codice_fiscale):
    """
    Validatore esteso che verifica che il codice fiscale sia valido.
    Se il codice fiscale e' temporaneo (11 cifre numeriche), e' considerato valido.
    :param codice_fiscale: Il codice fiscale.
    :return: None. Exception in caso di validazione.
    """
    try:
        codicefiscale.validate(codice_fiscale)
    except:
        if re.search("^[0-9]{11}$", codice_fiscale) is None:
            raise


def valida_codice_fiscale(codice_fiscale):
    try:
        _valida_codice_fiscale(codice_fiscale)
    except:
        raise ValidationError("Il codice fiscale non è valido.")


def ottieni_genere_da_codice_fiscale(codice_fiscale, default=None):
    try:
        return codicefiscale.get_gender(codice_fiscale)
    except:
        return default


def crea_validatore_dimensione_file(mb=10):

    def _validatore(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = mb
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))

    return _validatore


def valida_partita_iva(partita_iva):
    try:
        return stdnum.it.iva.validate(partita_iva)
    except:
        raise ValidationError("Partita IVA non corretta.")


def valida_iban(iban_no):
    from stdnum import iban
    try:
        return iban.validate(iban_no)
    except:
        raise ValidationError("IBAN non valido.")


def valida_dimensione_file_5mb(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 5
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))


def valida_dimensione_file_6mb(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 6
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))


def valida_dimensione_file_10mb(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 10
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))


def valida_dimensione_file_8mb(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 8
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))


def valida_almeno_14_anni(data):
    anni = 14
    al_giorno = timezone.now().date()
    if (al_giorno.year - data.year - ((al_giorno.month, al_giorno.day) < (data.month, data.day))) <  anni:
        raise ValidationError("Sono necessari almeno %d anni di età" % (anni,))


def valida_email_personale(email):
    coppie = (
        ('cl.', '@cri.it'),
        ('cp.', '@cri.it'),
        ('cr.', '@cri.it'),
    )
    for coppia in coppie:
        if email and email.lower().startswith(coppia[0]) and email.lower().endswith(coppia[1]):
            raise ValidationError("Non è possibile utilizzare una casella istituzionale come "
                                  "indirizzo e-mail personale.")


def valida_data_nel_passato(data):
    if isinstance(data, datetime):
        if data > datetime.now():
            raise ValidationError("Data ed ora non possono essere nel futuro.")
    elif isinstance(data, date):
        if data > date.today():
            raise ValidationError("La data non può essere nel futuro.")
    else:
        raise TypeError("Fornito tipo di data non valido.")


@deconstructible
class ValidateFileSize(object):
    def __init__(self, filesize=2):
        self.filesize = filesize

    def __call__(self, *args, **kwargs):
        file = args[0]
        filesize = file.file.size
        megabyte_limit = self.filesize
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError(
                "Seleziona un file più piccolo di %sMB" % str(megabyte_limit))
