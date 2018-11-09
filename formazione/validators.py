def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['zip', 'rar', '.pdf', '.doc', '.docx', '.jpg',
                        '.png', '.xlsx', '.xls']
    if ext.lower() not in valid_extensions:
        raise ValidationError("Estensione <%s> di questo file non è "
                              "accettabile." % ext)