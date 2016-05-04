# -*- coding: utf-8 -*-
from django.conf import settings
from filer.fields.file import FilerFileField as BaseFilerFileField
from filer.fields.image import FilerImageField as BaseFilerImageField
from filer.utils.loader import load_object

from .models import Documento, Immagine


class CampoDocumentoFiler(BaseFilerFileField):
    default_model_class = Documento


class CampoImmagineFiler(BaseFilerImageField):
    default_model_class = Immagine


# Questo è codice di compatibilità preso dalla versione più aggiornata di filer
def get_filer_image_field():
    base_field = getattr(settings, 'FILER_IMAGE_FIELD', 'filer.fields.image.FilerImageField')
    return load_object(base_field)


def get_filer_file_field():
    base_field = getattr(settings, 'FILER_FILE_FIELD', 'filer.fields.file.FilerFileField')
    return load_object(base_field)

FilerFileField = get_filer_file_field()
FilerImageField = get_filer_image_field()
