from django import template
from django.template.loader import render_to_string

from base.stringhe import genera_uuid_casuale
from donazioni.elenchi import ElencoDonatori

register = template.Library()


@register.filter(name='importo')
def importo(value=None):
    value = 0 if not value else value
    return '{0:.2f} €'.format(value)


@register.simple_tag(takes_context=True)
def elenco_donatori(context, oggetto_elenco=None,):

    if not isinstance(oggetto_elenco, ElencoDonatori):
        raise ValueError("Il tag elenco_donatori puo' solo essere usato con un oggetto Elenco, ma e' stato usato con un oggetto %s." % (oggetto_elenco.__class__.__name__,))

    elenco_id = genera_uuid_casuale()
    context.request.session["donatori_elenco_%s" % (elenco_id,)] = oggetto_elenco  # Passa elenco in sessione.

    context.update({
        'iframe_url': "/donazioni/donatori/ifrelenco/%s/1/" % (elenco_id,)
    })
    return render_to_string('us_elenchi_inc_iframe.html', context)
