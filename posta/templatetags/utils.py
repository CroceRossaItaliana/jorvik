from django.template import Library
from anagrafica.models import Delega
from anagrafica.permessi.applicazioni import PRESIDENTE


register = Library()


@register.filter
def nomina_presidenziale(tipo):
    return 'Presidente' if tipo == PRESIDENTE else 'Commissario'