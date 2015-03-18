from django.http import HttpResponse
from django.shortcuts import render, render_to_response

# Le viste base vanno qui.
from anagrafica.models import Comitato


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

