from django.template import Library
from attivita.models import Partecipazione, Attivita

register = Library()
@register.filter
def posso_vedere(attivita, persona):
    return Partecipazione.objects.filter(turno__attivita=attivita, persona=persona, confermata=True).exists()
