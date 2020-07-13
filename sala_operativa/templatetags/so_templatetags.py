from django.template import Library

from ..models import PartecipazioneSO, ServizioSO


register = Library()
@register.filter
def posso_vedere(servizio, persona):
    return PartecipazioneSO.objects.filter(
        turno__attivita=servizio,
        persona=persona,
        confermata=True
    ).exists()
