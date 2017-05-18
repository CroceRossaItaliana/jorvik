import newrelic.agent
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.http import urlencode
import functools
from anagrafica.permessi.costanti import ERRORE_ORFANO, ERRORE_PERMESSI
from base.menu import menu
from jorvik.settings import LOGIN_URL

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


def pagina_pubblica(funzione=None, permetti_embed=False):
    """
    Questa funzione attua da decoratore per le pagine accessibili sia a privati che pubblico.
    :param funzione: (decoratore)
    :return: (decoratore)
    """

    # Questo codice rende i parametri opzionali, ie. rende possibile chiamare sia @pagina_pubblica
    # che @pagina_pubblica(permetti_embed=True)
    if funzione is None:
        return functools.partial(pagina_pubblica, permetti_embed=permetti_embed)

    def _pagina_pubblica(request, *args, **kwargs):

        newrelic.agent.set_transaction_name(funzione.__name__, "pubblica")

        request.me = request.user.persona if request.user and hasattr(request.user, 'persona') else None
        (template, contesto, richiesta) = _spacchetta(funzione(request, request.me, *args, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        request_embed = request.GET.get('embed', default='False')
        embed = permetti_embed and request_embed.lower() in ('true', '1')

        contesto.update({"me": request.me})
        contesto.update({"embed": embed})
        contesto.update({"request": request})
        contesto.update({"menu": menu(request)})
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

        if request.user.is_authenticated():
            return redirect(pagina)

        (template, contesto, richiesta) = _spacchetta(funzione(request, *args, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        contesto.update({"me": None})
        contesto.update({"request": request})
        contesto.update({"menu": menu(request)})
        return render_to_response(template, RequestContext(request, contesto))

    return _pagina_anonima


def pagina_privata(funzione=None, pagina=LOGIN_URL, permessi=[]):
    """
    Questa funzione attua da decoratore per le pagine accessibili SOLO da utenti identificati.
    Redirect automatico a una pagina.
    :param funzione: (decoratore)
    :param pagina: Pagina verso il quale fare il redirect. Default: LOGIN_REDIRECT_URL.
    :param permessi: Un elenco di permessi NECESSARI.
    :return: (decoratore)
    """

    # Questo codice rende i parametri opzionali, ie. rende possibile chiamare sia @pagina_privata
    # che @pagina_privata(pagina=x) o @pagina_privata(permesso1, permesso2, ...)
    if funzione is None:
        return functools.partial(pagina_privata, pagina=pagina, permessi=permessi)

    def _pagina_privata(request, *args, **kwargs):

        newrelic.agent.set_transaction_name(funzione.__name__, "privata")

        if isinstance(request.user, AnonymousUser):
            return redirect(LOGIN_URL + "?" + urlencode({"next": request.path}))

        if not request.user or request.user.applicazioni_disponibili is None:
            return redirect(ERRORE_ORFANO)

        request.me = request.user.persona
        newrelic.agent.add_custom_parameter("persona_id", "%d" % (request.me.pk,))

        if not request.me.ha_permessi(permessi):  # Controlla che io lo abbia
            return redirect(ERRORE_PERMESSI)  # Altrimenti, buttami fuori

        (template, contesto, richiesta) = _spacchetta(funzione(request, request.me, *args, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        contesto.update({"me": request.me})
        contesto.update({"request": request})
        contesto.update({"menu": menu(request)})
        return render_to_response(template, RequestContext(request, contesto))

    return _pagina_privata


def pagina_privata_no_cambio_firma(funzione=None, pagina=LOGIN_URL, permessi=[]):
    """
    Questa funzione attua da decoratore per le pagine accessibili SOLO da utenti identificati.
    Redirect automatico a una pagina.

    Questa versione (_no_cambio_firma) non modifica la firma della funzione ...(request, **kwargs).
    Ideale per l'uso o estensione delle viste di Django.

    :param funzione: (decoratore)
    :param pagina: Pagina verso il quale fare il redirect. Default: LOGIN_REDIRECT_URL.
    :param permessi: Un elenco di permessi NECESSARI.
    :return: (decoratore)
    """

    # Questo codice rende i parametri opzionali, ie. rende possibile chiamare sia @pagina_privata
    # che @pagina_privata(pagina=x) o @pagina_privata(permesso1, permesso2, ...)
    if funzione is None:
        return functools.partial(pagina_privata, pagina=pagina, permessi=permessi)

    def _pagina_privata(request, *args, **kwargs):

        newrelic.agent.set_transaction_name(funzione.__name__, "privata")

        if isinstance(request.user, AnonymousUser):
            return redirect(LOGIN_URL)

        if not request.user or request.user.applicazioni_disponibili is None:
            return redirect(ERRORE_ORFANO)

        request.me = request.user.persona

        if not request.me.ha_permessi(permessi):  # Controlla che io lo abbia
            return redirect(ERRORE_PERMESSI)  # Altrimenti, buttami fuori

        extra = {}
        extra.update({"me": request.me})
        extra.update({"request": request})
        extra.update({"menu": menu(request)})

        (template, contesto, richiesta) = _spacchetta(funzione(request, *args, extra_context=extra, **kwargs))

        if template is None:  # Se ritorna risposta particolare (ie. Stream o Redirect)
            return richiesta  # Passa attraverso.

        contesto.update({"me": request.me})
        contesto.update({"request": request})
        contesto.update({"menu": menu(request)})
        return render_to_response(template, RequestContext(request, contesto))

    return _pagina_privata


class VistaDecorata(object):
    """
    Questo mixin permette di usare i decoratori sopra nelle class based views

    Per applicare i decoratori la vista deve essere costruita nel modo seguente:

    class ListaArticoli(VistaDecorata, ListView):
        ...

        @method_decorator(pagina_privata)
        def dispatch(self, request, *args, **kwargs):
            return super(ListaArticoli, self).dispatch(request, *args, **kwargs)
    """
    permetti_embed = False

    def contesto(self, contesto):
        embed = self.permetti_embed and self.request.GET.get('embed', default='false') == 'true'

        try:
            contesto.update({'me': self.request.me})
        except AttributeError:
            pass
        try:
            contesto.update({'menu': menu(self.request)})
        except AttributeError:
            pass
        contesto.update({'embed': embed})
        return contesto

    def get_context_data(self, **kwargs):
        return self.contesto(super(VistaDecorata, self).get_context_data(**kwargs))
