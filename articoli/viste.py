from django.shortcuts import render
from django.views.generic import DetailView, ListView

from articoli.models import Articolo
from autenticazione.funzioni import pagina_privata, pagina_pubblica


class ListaArticoli(ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'

    def get_queryset(self):
        return Articolo.objects.pubblicati()


class DettaglioArticolo(DetailView):
    model = Articolo
    slug_field = 'pk'
    slug_url_kwarg = 'articolo_pk'
    context_object_name = 'articolo'
    template_name = 'dettaglio_articolo.html'
