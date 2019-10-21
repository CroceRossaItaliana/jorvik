from django.template import Library
from attivita.models import Partecipazione, Attivita

register = Library()
@register.filter
def posso_vedere(attivita, persona):
    return Partecipazione.objects.filter(turno__attivita=attivita, persona=persona, confermata=True).exists()


@register.filter
def dammi(json, key):
    return json[key]

@register.filter
def parse_girni(l):
    parse = {1: 'Lunedì', 2: 'Martedì', 3: 'Mercoledì', 4: 'Giovedì',  5: 'Venerdì', 6: 'Sabato', 7: 'Domenica'}
    return parse[l]