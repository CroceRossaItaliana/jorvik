# -*- coding: utf-8 -*-
from django import template
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