import datetime
from django.core.exceptions import ValidationError

__author__ = 'alfioemanuele'

def valida_data_manutenzione(data):
        if data > datetime.date.today():
            raise ValidationError("La manutenzione non può essere nel futuro")