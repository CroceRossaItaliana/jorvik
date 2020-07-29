from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse


from anagrafica.permessi.costanti import (ERRORE_PERMESSI, GESTIONE_SO_SEDE, )

from autenticazione.funzioni import pagina_privata
from base.utils import poco_fa
# from .forms import (VolontarioReperibilitaForm, ServizioSOAggiungiForm,
#     AggiungiReperibilitaPerVolontarioForm, )
from .models import ReperibilitaSO, ServizioSO



"""
from django.conf.urls import url
from . import views as so_views


pk = "(?P<pk>[0-9]+)"

app_label = 'so'
urlpatterns = [
    url(r'^$', so_views.sala_operativa_index, name='index'),

    # Reperibilita
    url(r'^r/$', so_views.sala_operativa_reperibilita, name='reperibilita'),
    url(r'^r/backup/$', so_views.sala_operativa_reperibilita_backup, name='reperibilita_backup'),
    url(r'^r/%s/delete/$' % pk, so_views.sala_operativa_reperibilita_cancella, name='reperibilita_cancella'),
    url(r'^r/%s/edit/$' % pk, so_views.sala_operativa_reperibilita_edit, name='reperibilita_modifica'),

    # Servizi
    url(r'^s/$', so_views.sala_operativa_servizi, name='servizi'),
    url(r'^s/add/$', so_views.sala_operativa_servizi_aggiungi, name='servizio_aggiungi'),
    url(r'^s/%s/$' % pk, so_views.sala_operativa_servizio_dettagli, name='servizio_dettagli'),
    url(r'^s/%s/edit/$' % pk, so_views.sala_operativa_servizio_edit, name='servizio_modifica'),
    url(r'^s/%s/delete/$' % pk, so_views.sala_operativa_servizio_cancella, name='servizio_cancella'),
    url(r'^s/%s/add/vo/(?P<reperibilita_pk>[0-9]+)/$' % pk, so_views.sala_operativa_servizio_abbina_vo, name='servizio_add_vo'),
    url(r'^s/%s/remove/vo/(?P<reperibilita_pk>[0-9]+)/$' % pk, so_views.sala_operativa_servizio_rimuovi_vo, name='togli_dal_servizio'),

    # Turni
    url(r'^t/$', so_views.sala_operativa_turni, name='turni'),

    # Poteri
    url(r'^p/$', so_views.sala_operativa_poteri, name='poteri'),
]
"""

@pagina_privata
def sala_operativa_turni(request, me):
    """
    Il volontario vede i suoi turni approvati.
    """

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
def sala_operativa_servizi(request, me):
    """
    todo:
    SOL: Può estrarre i dati locali
    SOR: Può estrarre i dati locali, regionali
    SON: Può estrarre i dati locali, regionali, nazionali
    """

    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
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
    sedi = me.oggetti_permesso(GESTIONE_SO_SEDE)
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
def sala_operativa_servizio_edit(request, me, pk):
    servizio = get_object_or_404(ServizioSO, pk=pk)
    if servizio.creato_da != me:
        return redirect(ERRORE_PERMESSI)
    form = ServizioSOAggiungiForm(request.POST or None, instance=servizio)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('so:reperibilita_backup'))
    context = {
        'form': form,
        'servizio': servizio,
    }
    return 'sala_operativa_servizio_edit.html', context


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


@pagina_privata
def sala_operativa_approva_attivazioni(request, me):
    pass


@pagina_privata
def sala_operativa_visualizza_attestati(request, me):
    pass


@pagina_privata
def sala_operativa_proposta_edit_odp(request, me):
    pass


@pagina_privata
def sala_operativa_approva_proposte_edit_odp(request, me):
    pass


@pagina_privata
def sala_operativa_visualizza_proposte_edit_odp(request, me):
    pass
