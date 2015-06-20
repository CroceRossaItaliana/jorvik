from django.shortcuts import render_to_response
from django.template import RequestContext

__author__ = 'alfioemanuele'


def pagina_pubblica(funzione):
    """
    Questa funzione attua da decoratore per le pagine accessibili sia a privati che pubblico.
    :param funzione:
    :return:
    """

    def _pagina_pubblica(request, *args, **kwargs):
        r = funzione(request, *args, **kwargs)

        # Controlla se tupla (pagina, contesto) oppure solo 'pagina.html'.
        if isinstance(r, tuple):
            (html, contesto) = r
        else:
            (html, contesto) = (r, {})
        return render_to_response(html, RequestContext(request, contesto))

    return _pagina_pubblica
