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


@register.assignment_tag(takes_context=True)
def partecipazione(context, turno):
    """ Controlla lo stato di partecipazione tra turno e il servizio """

    if not hasattr(context.request, 'me'):
        return turno.TURNO_NON_PUOI_PARTECIPARE_ACCEDI

    return turno.persona(context.request.me)


@register.simple_tag
def mezzo_prenotato_per_servizio(mezzo, servizio):
    if servizio in mezzo.abbinato_ai_servizi():
        return True
    return False
