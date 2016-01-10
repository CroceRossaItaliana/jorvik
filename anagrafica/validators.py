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
