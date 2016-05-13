# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def bool(value):
    if value:
        return 'true'
    else:
        return 'false'