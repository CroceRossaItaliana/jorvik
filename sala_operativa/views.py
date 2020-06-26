from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from anagrafica.permessi.costanti import (ERRORE_PERMESSI,
    GESTIONE_SALA_OPERATIVA_SEDE, GESTIONE_POTERI_SALA_OPERATIVA_SEDE)

from autenticazione.funzioni import pagina_privata
from base.utils import poco_fa
from .forms import (VolontarioReperibilitaForm, ServizioSOAggiungiForm,
    AggiungiReperibilitaPerVolontarioForm, )
from .models import ReperibilitaSO, ServizioSO


INITIAL_INIZIO_FINE_PARAMS = {
    "inizio": poco_fa() + timedelta(hours=1),
    "fine": poco_fa() + timedelta(hours=2),
}

@pagina_privata
def sala_operativa_index(request, me):
    if not me.volontario:
        return redirect('/')

    sedi = me.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    if not sedi:
        return redirect(reverse('so:reperibilita'))

    context = {
        'ora': poco_fa(),
        'sedi': sedi,
        'reperibilita': ReperibilitaSO.reperibilita_per_sedi(sedi),
    }
    return 'sala_operativa_index.html', context


@pagina_privata
def sala_operativa_reperibilita(request, me):
    if not me.volontario:
        return redirect('/')

    form = VolontarioReperibilitaForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
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
    if me not in [reperibilita.persona, reperibilita.creato_da, ]:
        return redirect(ERRORE_PERMESSI)
    reperibilita.delete()
    messages.success(request, 'La reperibilita selezionata è stata rimossa.')
    return redirect(reverse('so:reperibilita'))


@pagina_privata
def sala_operativa_reperibilita_edit(request, me, r_pk):
    if not me.volontario:
        return redirect('/')

    reperibilita = get_object_or_404(ReperibilitaSO, pk=r_pk)
    if reperibilita.creato_da != me:
        return redirect(ERRORE_PERMESSI)

    form = VolontarioReperibilitaForm(request.POST or None, instance=reperibilita)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('so:reperibilita_backup'))
    context = {
        'form': form,
        'reperibilita': reperibilita,
    }
    return 'sala_operativa_reperibilita_edit.html', context


@pagina_privata
def sala_operativa_reperibilita_backup(request, me):
    form = AggiungiReperibilitaPerVolontarioForm(request.POST or None, initial=INITIAL_INIZIO_FINE_PARAMS)
    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            reperibilita = form.save(commit=False)
            reperibilita.persona = cd['persona']
            reperibilita.creato_da = me
            reperibilita.save()
            return redirect(reverse('so:reperibilita_backup'))

    context = {
        'form': form,
        'reperibilita': ReperibilitaSO.reperibilita_create_da(me),
    }
    return 'sala_operativa_reperibilita_per_volontario_aggiungi.html', context


@pagina_privata
def sala_operativa_servizi(request, me):
    sedi = me.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    if not sedi:
        return redirect(reverse('so:reperibilita'))

    # print(sedi.values_list('pk', 'estensione'))

    servizi_qs = ServizioSO.objects.filter(creato_da=me)

    context = {
        'form': ServizioSOAggiungiForm(),
        'servizi': servizi_qs,
    }

    return 'sala_operativa_servizi.html', context


@pagina_privata
def sala_operativa_servizio_dettagli(request, me, pk):
    sedi = me.oggetti_permesso(GESTIONE_SALA_OPERATIVA_SEDE)
    if not sedi:
        return redirect('/')

    servizio = get_object_or_404(ServizioSO, pk=pk)
    reperibilita_volontari_qs = ReperibilitaSO.reperibilita_per_sedi(sedi)

    context = {
        'servizio': servizio,
        'reperibilita_volontari': reperibilita_volontari_qs,
    }

    return 'sala_operativa_servizio_dettagli.html', context


@pagina_privata
def sala_operativa_servizio_cancella(request, me, pk):
    if not me.volontario:
        return redirect('/')
    servizio = get_object_or_404(ServizioSO, pk=pk)
    if me not in [servizio.creato_da, ]:
        return redirect(ERRORE_PERMESSI)
    servizio.delete()
    messages.success(request, 'Il servizio è stato rimosso.')
    return redirect(reverse('so:servizi'))


@pagina_privata
def sala_operativa_servizi_aggiungi(request, me):
    context = {}

    form = ServizioSOAggiungiForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            servizio = form.save(commit=False)
            servizio.creato_da = me
            servizio.save()

            messages.success(request, 'Servizio inserito con successo')
            return redirect(reverse('so:servizi'))

    return 'sala_operativa_servizi_aggiungi.html', context


@pagina_privata
def sala_operativa_servizio_abbina_vo(request, me, pk, reperibilita_pk=None):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    reperibilita_di_persona = ReperibilitaSO.objects.get(pk=reperibilita_pk)

    if servizio not in reperibilita_di_persona.servizio.all():
        reperibilita_di_persona.servizio.add(servizio)
        reperibilita_di_persona.fine = servizio.fine
        reperibilita_di_persona.save()
        messages.success(request, 'Il volontario è stato abbinato al servizio.')
        return redirect(reverse('so:servizio_dettagli', args=[pk,]))

    return redirect(reverse('so:servizi'))


@pagina_privata
def sala_operativa_servizio_rimuovi_vo(request, me, pk, reperibilita_pk):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    reperibilita_di_persona = ReperibilitaSO.objects.get(pk=reperibilita_pk)

    if servizio in reperibilita_di_persona.servizio.all():
        reperibilita_di_persona.servizio.remove(servizio)
        reperibilita_di_persona.save()
        messages.success(request, 'Il volontario è stato rimosso dal servizio.')
        return redirect(reverse('so:servizio_dettagli', args=[pk,]))

    return redirect(reverse('so:servizi'))
