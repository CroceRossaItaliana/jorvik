# -*- coding: utf-8 -*-
from django import template
from django.contrib.messages import constants
from django.utils.six import string_types

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
