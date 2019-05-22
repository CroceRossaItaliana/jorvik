# -*- coding: utf-8 -*-
from datetime import datetime
from django import template
from django.contrib.messages import constants
from django.utils.six import string_types
from anagrafica.permessi.costanti import PRESIDENTE, COMMISSARIO

register = template.Library()


@register.filter
def bool(value):
    if value:
        return 'true'
    else:
        return 'false'

@register.simple_tag(takes_context=True)
def show_test_users_with_credentials(context):
    from anagrafica.models import Persona
    from django.utils.safestring import mark_safe

    try:
        request = context['request']
        host = request.build_absolute_uri()

        if "provami.gaia.cri.it" in host or "127.0.0.1" in host:
            vo = Persona.objects.filter(nome__istartswith='volontario_').last()
            pr = Persona.objects.filter(nome__istartswith='presidente_').last()

            html = ''
            if vo:
                html = "<div>%s : %s</div>" % (vo.utenza, vo.utenza.check_password(vo.utenza.email))
            if pr:
                html += "<div>%s : %s</div>" % (pr.utenza, pr.utenza.check_password(pr.utenza.email))

            return mark_safe(html)
    except:
        # per escludere qualsiasi exception
        pass


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, string_types):
        return text.startswith(starts)
    return False


@register.filter('level_to_bootstrap')
def level_to_bootstrap(message):
    map = {
        constants.DEBUG: 'alert-info',
        constants.INFO: 'alert-info',
        constants.SUCCESS: 'alert-success',
        constants.WARNING: 'alert-warning',
        constants.ERROR: 'alert-danger',
    }
    return map.get(message.level, 'alert-info')


@register.filter
def select_nomina_presidenziale(sede):
    delega_presidenziale= sede.deleghe_attuali(
        al_giorno=datetime.now(), tipo=PRESIDENTE, fine=None
    ).first()

    if delega_presidenziale:
        return 'Presidente'

    delega_presidenziale = sede.deleghe_attuali(
        al_giorno=datetime.now(), tipo=COMMISSARIO, fine=None
    ).first()

    if delega_presidenziale:
        return 'Commissario'
    # Caso in cui non ci sono delegati
    else:
        return ''