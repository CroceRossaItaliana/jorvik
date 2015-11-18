from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from anagrafica.permessi.costanti import MODIFICA
from social.models import Commento

register = template.Library()


@register.simple_tag(takes_context=True)
def commenti(context, oggetto=None, numero=20, altezza_massima=None):

    if not hasattr(oggetto, 'commenti'):
        raise ValueError("Oggetto (%s) non valido (senza Mixin ConCommenti)" % (str(oggetto),))

    if numero < 1 or numero > 100:
        raise ValueError("Numero (%d) non valido (1 < n < 200)" % (numero,))

    next = context['request'].path
    oggetto_tipo = ContentType.objects.get_for_model(oggetto)
    commenti = oggetto.commenti.all().order_by('-creazione')[0:numero]
    for commento in commenti:
        if hasattr(context['request'], 'me'):
            commento.puo_modificare = context['request'].me == commento.autore \
                                      or context['request'].me.permessi_almeno(oggetto, MODIFICA)

    context.update({
        'social_commenti': commenti,
        'social_next': next,
        'social_oggetto': oggetto,
        'social_oggetto_app_label': oggetto_tipo.app_label,
        'social_oggetto_model': oggetto_tipo.model,
        'social_lunghezza_massima': Commento.LUNGHEZZA_MASSIMA,
        'social_altezza_massima': altezza_massima,
    })

    return render_to_string('social_commenti_tag_elenco.html', context)