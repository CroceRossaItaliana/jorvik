def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['zip', 'rar', '.pdf', '.doc', '.docx', '.jpg',
                        '.png', '.xlsx', '.xls']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Estensione <%s> di questo file non è "
                              "accettabile." % ext)


def course_file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course/<course_id>
    return 'courses/%s/%s' % (instance.id, filename)


def delibera_file_upload_path(instance, filename):
    return 'courses/delibere/%s' % (filename,)


def evento_file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/course/<course_id>
    return 'evento/%s/%s' % (instance.id, filename)
