from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone


def valida_data_non_nel_futuro(data):
    if isinstance(data, datetime):
        ora = timezone.now()
    else:
        ora = timezone.now().date()
    if data > ora:
        raise ValidationError("La data non può essere nel futuro.")
