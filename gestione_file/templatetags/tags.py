from django.template import Library

register = Library()

@register.filter
def posso_vedere(documento_sede, sede):
    return documento_sede == sede
