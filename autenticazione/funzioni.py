from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from jorvik.settings import LOGIN_REDIRECT_URL

__author__ = 'alfioemanuele'


def _spacchetta(pacchetto):
    # Controlla se tupla (pagina, contesto) oppure solo 'pagina.html'.
    if isinstance(pacchetto, tuple):
        (template, contesto, richiesta) = pacchetto + (pacchetto, )
    elif isinstance(pacchetto, str):
        (template, contesto, richiesta) = (pacchetto, {}, pacchetto)
    else:
        (template, contesto, richiesta) = (None, None, pacchetto)
    return template, contesto, richiesta


def pagina_pubblica(funzione):
    """
    Questa funzione attua da decoratore per le pagine accessibili sia a privati che pubblico.
    :param funzione: (decoratore)
    :return: (decoratore)
    """

    def _pagina_pubblica(request, *args, **kwargs):

        (template, contesto, richiesta) = _spacchetta(funzione(request, *args, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        return render_to_response(template, RequestContext(request, contesto))

    return _pagina_pubblica


def pagina_anonima(funzione, pagina='/utente/'):
    """
    Questa funzione attua da decoratore per le pagine accessibili SOLO da utenti anonimi.
    Redirect automatico a una pagina.
    :param funzione: (decoratore)
    :param pagina: Pagina verso il quale fare il redirect. Default: "/utente/".
    :return: (decoratore)
    """

    def _pagina_anonima(request, *args, **kwargs):

        (template, contesto, richiesta) = _spacchetta(funzione(request, *args, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        if request.user.is_authenticated():
            return redirect(pagina)

        return render_to_response(template, RequestContext(request, contesto))

    return _pagina_anonima


def pagina_privata(funzione, pagina=LOGIN_REDIRECT_URL):
    """
    Questa funzione attua da decoratore per le pagine accessibili SOLO da utenti identificati.
    Redirect automatico a una pagina.
    :param funzione: (decoratore)
    :param pagina: Pagina verso il quale fare il redirect. Default: LOGIN_REDIRECT_URL.
    :return: (decoratore)
    """

    return login_required(funzione, login_url=pagina)
