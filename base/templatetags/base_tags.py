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


@register.simple_tag(takes_context=True)
def current_domain(context):
    request = context.get('request')
    if request:
        uri = request.build_absolute_uri('/')
        return uri[:-1] if uri.endswith('/') else uri
    return ""
