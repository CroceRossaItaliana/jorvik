import magic
import os
from django.core.exceptions import ValidationError
from anagrafica.costanti import MIMETYPE_TO_CHECK

files_supportati = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['zip', 'rar', '.pdf', '.doc', '.docx', '.jpg', '.jpeg','.gif',
                        '.png', '.xlsx', '.xls']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Estensione <%s> di questo file non è "
                              "accettabile." % ext)


def validate_file_mime_type(value):#per le immagini
    mime = magic.from_buffer(value.read(), mime=True)
    if mime not in files_supportati:
        raise ValidationError("Estensione <%s> di questo file non è "
                              "accettabile." % mime)

def validate_file_type(value):
    try:
        validate_file_extension(value)
    except:
        return False
    file_supportati=MIMETYPE_TO_CHECK+files_supportati
    mime = magic.from_buffer(value.read(), mime=True)
    if mime not in file_supportati:
        return False
#        raise ValidationError("Estensione <%s> di questo file non è "
#                              "accettabile." % mime)
    return True

def validate_file_type_for_model(value):
    try:
        validate_file_extension(value)
    except:
        raise ValidationError("Tipo di file non supportato. Tipi di file supportati: csv, zip, rar, gif, png, jpg,  jpeg, tiff, rtf, pdf, ods, odt, doc, docx, xls, xlsx.")
    file_supportati=MIMETYPE_TO_CHECK+files_supportati
    mime = magic.from_buffer(value.read(), mime=True)
    if mime not in file_supportati:
        raise ValidationError("Estensione <%s> di questo file non è "
                              "accettabile." % mime)



def course_file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course/<course_id>
    return 'courses/%s/%s' % (instance.id, filename)


def delibera_file_upload_path(instance, filename):
    return 'courses/delibere/%s' % (filename,)


def evento_file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course/<course_id>
    return 'evento/%s/%s' % (instance.id, filename)
