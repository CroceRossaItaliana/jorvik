from django.http import HttpResponse
from django.shortcuts import render, render_to_response

# Le viste base vanno qui.
from django.template import RequestContext
from anagrafica.models import Comitato
from base.forms import ModuloRecuperaPassword


def index(request):
    contesto = {
        'numero_comitati': Comitato.objects.count(),
    }
    return render_to_response('base_home.html', contesto)


def manutenzione(request):
    """
    Mostra semplicemente la pagina di manutenzione ed esce.
    """
    return render_to_response('base_manutenzione.html', {})


def recupera_password(request):
    """
    Mostra semplicemente la pagina di recupero password.
    """
    if request.method == 'POST':
        modulo = ModuloRecuperaPassword(request.POST)
        if modulo.is_valid():
            pass
            # TODO RECUPERO
    else:
        contesto = {
            'modulo': ModuloRecuperaPassword(),
        }
        return render_to_response('base_recupera_password.html', RequestContext(request, contesto))

def informazioni(request):
    """
    Mostra semplicemente la pagina diinformazioni ed esce.
    """
    return render_to_response('base_informazioni.html', {})


def aggiornamenti(request):
    """
    Mostra semplicemente la pagina degli aggiornamenti ed esce.
    """
    return render_to_response('base_informazioni_aggiornamenti.html', {})