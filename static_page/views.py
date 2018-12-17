from django.shortcuts import render, redirect, get_object_or_404
from autenticazione.funzioni import pagina_privata
from .models import Page


@pagina_privata
def view_page(request, me, slug):
    return 'articolo_view.html', {
        'page': get_object_or_404(Page, slug=slug),
    }
