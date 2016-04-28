from django.shortcuts import render

from articoli.models import Articolo
from autenticazione.funzioni import pagina_privata, pagina_pubblica


@pagina_privata
def lista_articoli(request, me):
    pass

@pagina_privata
def dettaglio_articolo(request, me):
    pass