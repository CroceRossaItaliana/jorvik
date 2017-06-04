from datetime import datetime
from itertools import chain

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404

from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA, COMPLETO, ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from donazioni.forms import ModuloCampagna, ModuloEtichetta
from donazioni.models import Campagna, Etichetta


@pagina_privata
def donazioni_home(request, me):
    contesto = {
        'sedi': me.oggetti_permesso(GESTIONE_CAMPAGNE),
        'campagne': me.oggetti_permesso(GESTIONE_CAMPAGNA),
    }
    template = 'donazioni.html'
    return template, contesto


@pagina_privata
def campagne_elenco(request, me):
    contesto = {
        "campagne": me.oggetti_permesso(GESTIONE_CAMPAGNA),
        "puo_creare": me.ha_permesso(GESTIONE_CAMPAGNE),
    }
    template = 'donazioni_campagne_elenco.html'
    return template, contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def campagna_nuova(request, me):

    sedi_campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
    etichette_qs = Etichetta.query_etichette_comitato(sedi_campagne_qs)

    modulo = ModuloCampagna(request.POST or None, initial={"inizio": datetime.now()})
    modulo.fields['organizzatore'].queryset = sedi_campagne_qs
    modulo.fields['etichette'].queryset = etichette_qs

    if modulo.is_valid():
        campagna = modulo.save()
        request.session['campagna_creata'] = campagna.pk
        return redirect(campagna.url_responsabili)

    contesto = {
        "modulo": modulo
    }
    return 'donazioni_campagna_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def campagna_modifica(request, me, pk):
    campagna_obj = get_object_or_404(Campagna, pk=pk)
    modulo = ModuloCampagna(request.POST or None, instance=campagna_obj)
    if modulo.is_valid():
        campagna = modulo.save()
        return redirect(campagna.url)
    sedi_campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
    etichette_qs = Etichetta.query_etichette_comitato(sedi_campagne_qs)
    modulo.fields['organizzatore'].queryset = sedi_campagne_qs
    modulo.fields['etichette'].queryset = etichette_qs
    contesto = {
        "modulo": modulo
    }
    return 'donazioni_campagna_modifica.html', contesto


@pagina_privata
def campagna_elimina(request, me, pk):
    campagna_obj = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna_obj, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    campagna_obj.delete()
    return redirect(reverse('donazioni_campagne'))


@pagina_privata
def campagna(request, me, pk):
    campagna_obj = get_object_or_404(Campagna, pk=pk)
    puo_modificare = me.permessi_almeno(campagna_obj, MODIFICA)

    contesto = {
        "campagna": campagna_obj,
        "puo_modificare": puo_modificare,
    }
    return 'donazioni_campagna_scheda.html', contesto


@pagina_privata
def campagna_fine(request, me, pk):
    campagna_obj = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna_obj, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in campagna_obj.responsabili_attuali():  # Se sono responsabile
        redirect(campagna_obj.url)

    contesto = {
        "campagna": campagna_obj,
    }
    return 'donazioni_campagna_fine.html', contesto


@pagina_privata
def campagna_responsabili(request, me, pk):
    campagna_obj = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna_obj, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    continua_url = campagna_obj.url

    if 'campagna_creata' in request.session and int(request.session['campagna_creata']) == int(pk):
        continua_url = "/donazioni/campagne/%d/fine/" % (int(pk),)
        del request.session['campagna_creata']

    contesto = {
        "delega": RESPONSABILE_CAMPAGNA,
        "campagna": campagna_obj,
        "continua_url": continua_url
    }

    return 'donazioni_campagna_responsabili.html', contesto


# ######## ETICHETTE #################

@pagina_privata
def etichetta(request, me, pk):
    etichetta_obj = get_object_or_404(Etichetta, pk=pk)

    contesto = {
        "etichetta": etichetta_obj,
        "puo_modificare": me.ha_permesso(GESTIONE_CAMPAGNE),
    }
    return 'donazioni_etichetta_scheda.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def etichetta_nuova(request, me):
    sedi_campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
    modulo = ModuloEtichetta(request.POST or None)
    modulo.fields['comitato'].queryset = sedi_campagne_qs

    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect('donazioni_etichette')

    contesto = {
        "modulo": modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def etichetta_modifica(request, me, pk):
    etichetta_obj = get_object_or_404(Etichetta, pk=pk)
    modulo = ModuloEtichetta(request.POST or None, instance=etichetta_obj)
    sedi_campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNE)
    modulo.fields['comitato'].queryset = sedi_campagne_qs
    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect('donazioni_etichette')
    contesto = {
        "modulo": modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata
def etichetta_elimina(request, me, pk):
    if not me.ha_permessi(GESTIONE_CAMPAGNE):
        return redirect(ERRORE_PERMESSI)
    etichetta_obj = get_object_or_404(Etichetta, pk=pk)
    etichetta_obj.delete()
    return redirect(reverse('donazioni_etichette'))


@pagina_privata
def etichette_elenco(request, me):
    comitati = me.sedi_attuali().values_list('id', flat=True)
    sedi_deleghe_campagne = me.oggetti_permesso(GESTIONE_CAMPAGNE).values_list('id', flat=True)
    campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    filtro_etichette = Q(comitato__in=chain(comitati, sedi_deleghe_campagne)) | Q(campagne__in=campagne_qs)
    contesto = {
        "etichette": Etichetta.objects.filter(filtro_etichette).distinct(),
        'puo_modificare': me.ha_permessi(GESTIONE_CAMPAGNE)
    }
    template = 'donazioni_etichette_elenco.html'
    return template, contesto
