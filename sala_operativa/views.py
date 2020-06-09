from django.shortcuts import render

from autenticazione.funzioni import pagina_privata


@pagina_privata
def sala_operativa_index(request, me):
    context = dict()
    return 'sala_operativa_index.html', context


@pagina_privata
def sala_operativa_reperibilita(request, me):
    context = dict()
    return 'sala_operativa_reperibilita.html', context


@pagina_privata
def sala_operativa_turni(request, me):
    context = dict()
    return 'sala_operativa_turni.html', context


@pagina_privata
def sala_operativa_poteri(request, me):
    context = dict()
    return 'sala_operativa_poteri.html', context
