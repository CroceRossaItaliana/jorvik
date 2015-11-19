from django.template import Library
from django.template.loader import render_to_string

from anagrafica.models import Persona

register = Library()


@register.simple_tag(takes_context=True)
def card(context, persona=None, nome=True, extra_class="btn btn-sm btn-default", avatar=False):

    if not isinstance(persona, Persona):
        raise ValueError("Il tag card puo' solo essere usato con una persona, ma e' stato usato con un oggetto %s." % (persona.__class__.__name__,))

    context.update({
        'card_persona': persona,
        'card_nome': nome,
        'card_avatar': avatar,
        'card_class': extra_class,
    })

    return render_to_string('anagrafica_tags_card.html', context)
