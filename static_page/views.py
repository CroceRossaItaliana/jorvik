from django.shortcuts import render, redirect, get_object_or_404
from autenticazione.funzioni import pagina_privata
from .models import Page


@pagina_privata
def view_page(request, me, slug):
    context = {
        'page': get_object_or_404(Page, slug=slug),
    }
    if slug in ['portale-convenzioni', 'report-violence']:
        context['has_privacy_popup'] = True

    return 'page_view.html', context
