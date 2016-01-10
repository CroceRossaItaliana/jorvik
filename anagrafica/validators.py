from django.utils import timezone
from stdnum.it import codicefiscale
from django.core.exceptions import ValidationError


def valida_codice_fiscale(codice_fiscale):
    try:
        codicefiscale.validate(codice_fiscale)
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


def valida_dimensione_file_5mb(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 5
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
