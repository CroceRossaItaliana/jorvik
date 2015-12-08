from django.template import Library
from django.template.loader import render_to_string

from anagrafica.models import Persona
from anagrafica.permessi.costanti import PERMESSI_TESTO, NESSUNO
from base.stringhe import genera_uuid_casuale
from ufficio_soci.elenchi import Elenco

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


@register.simple_tag(takes_context=True)
def elenco(context, oggetto_elenco=None,):

    if not isinstance(oggetto_elenco, Elenco):
        raise ValueError("Il tag elenco puo' solo essere usato con un oggetto Elenco, ma e' stato usato con un oggetto %s." % (oggetto_elenco.__class__.__name__,))

    elenco_id = genera_uuid_casuale()
    context.request.session["elenco_%s" % (elenco_id,)] = oggetto_elenco  # Passa elenco in sessione.

    context.update({
        'iframe_url': "/us/elenco/%s/1/" % (elenco_id,)
    })
    return render_to_string('us_elenchi_inc_iframe.html', context)


@register.assignment_tag(takes_context=True)
def permessi_almeno(context, oggetto, minimo="lettura"):
    """
    Controlla che l'utente attuale -estrapolato dal contesto- abbia i permessi
     minimi su un determinato oggetto. Ritorna True o False.
    """

    if minimo not in PERMESSI_TESTO:
        raise ValueError("Permesso '%s' non riconosciuto. Deve essere in 'PERMESSI_TESTO'." % (minimo,))

    minimo_int = PERMESSI_TESTO[minimo]

    if minimo_int == NESSUNO:
        return True

    if not hasattr(context.request, 'me'):
        return False

    almeno = context.request.me.permessi_almeno(oggetto, minimo_int)
    return almeno

