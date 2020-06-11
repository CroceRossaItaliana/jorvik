from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from anagrafica.permessi.costanti import (ERRORE_PERMESSI,
    GESTIONE_SALA_OPERATIVA_SEDE, GESTIONE_POTERI_SALA_OPERATIVA_SEDE)


from autenticazione.funzioni import pagina_privata
from base.utils import poco_fa
from .forms import VolontarioReperibilitaForm
from .models import ReperibilitaSO


@pagina_privata
def sala_operativa_index(request, me):
    if not me.volontario:
        return redirect('/')

    sedi = me.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    if not sedi:
        return redirect(reverse('so:reperibilita'))

    context = {
        'ora': poco_fa(),
    }
    return 'sala_operativa_index.html', context


@pagina_privata
def sala_operativa_reperibilita(request, me):
    if not me.volontario:
        return redirect('/')

    form = VolontarioReperibilitaForm(request.POST or None, initial={
        "inizio": poco_fa() + timedelta(hours=1),
        "fine": poco_fa() + timedelta(hours=2),
    })

    if request.method == 'POST':
        if form.is_valid():
            reperibilita = form.save(commit=False)
            reperibilita.persona = me
            reperibilita.save()
            return redirect(reverse('so:reperibilita'))

    context = {
        'form': form,
        'reperibilita': ReperibilitaSO.reperibilita_di(me)[:50],
    }
    return 'sala_operativa_reperibilita.html', context


@pagina_privata
def sala_operativa_turni(request, me):
    if not me.volontario:
        return redirect('/')

    context = dict()
    return 'sala_operativa_turni.html', context


@pagina_privata
def sala_operativa_poteri(request, me):
    if not me.volontario:
        return redirect('/')

    context = dict()
    return 'sala_operativa_poteri.html', context


@pagina_privata
def sala_operativa_reperibilita_cancella(request, me, r_pk):
    if not me.volontario:
        return redirect('/')
    reperibilita = get_object_or_404(ReperibilitaSO, pk=r_pk)
    if not reperibilita.persona == me:
        return redirect(ERRORE_PERMESSI)
    reperibilita.delete()
    messages.success(request, 'La reperibilita selezionata è stata rimossa.')
    return redirect(reverse('so:reperibilita'))
