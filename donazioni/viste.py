from datetime import datetime
from itertools import chain

from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.shortcuts import redirect, get_object_or_404

from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from anagrafica.permessi.costanti import GESTIONE_CAMPAGNE, GESTIONE_CAMPAGNA, COMPLETO, ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from donazioni.forms import ModuloCampagna, ModuloEtichetta, ModuloFiltraCampagnePerEtichetta, ModuloDonazione, ModuloDonatore
from donazioni.models import Campagna, Etichetta, Donatore, Donazione


@pagina_privata
def donazioni_home(request, me):
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    donatori = Donatore.objects.filter(donazioni__campagna__in=campagne)
    fondi_raccolti = Donazione.objects.filter(campagna__in=campagne).aggregate(totale=Sum('importo'))
    contesto = {
        'sedi': me.oggetti_permesso(GESTIONE_CAMPAGNE),
        'campagne': campagne,
        'donatori': donatori,
        'fondi_raccolti': fondi_raccolti['totale']
    }
    return 'donazioni.html', contesto


@pagina_privata
def campagne_elenco(request, me):
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA).annotate(totale_donazioni=Sum('donazioni__importo'))
    modulo = ModuloFiltraCampagnePerEtichetta(request.POST or None, empty_permitted=True)
    if modulo.is_valid() and modulo.cleaned_data['etichette']:
        campagne = campagne.filter(etichette__in=modulo.cleaned_data['etichette'])
    contesto = {
        "campagne": campagne,
        "puo_creare": me.ha_permesso(GESTIONE_CAMPAGNE),
        "modulo_filtro": modulo,
    }
    return 'donazioni_campagne_elenco.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def campagna_nuova(request, me):

    modulo = ModuloCampagna(request.POST or None, initial={"inizio": datetime.now()})

    if modulo.is_valid():
        campagna = modulo.save()
        request.session['campagna_creata'] = campagna.pk
        return redirect(campagna.url_responsabili)

    contesto = {
        "modulo": modulo
    }
    return 'donazioni_campagna_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNA,))
def campagna_modifica(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloCampagna(request.POST or None, instance=campagna)

    if modulo.is_valid():
        campagna = modulo.save()
        return redirect(campagna.url)

    contesto = {
        'modulo': modulo
    }
    return 'donazioni_campagna_modifica.html', contesto


@pagina_privata
def campagna_elimina(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    campagna.delete()
    return redirect(reverse('donazioni_campagne'))


@pagina_privata
def campagna(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    puo_modificare = me.permessi_almeno(campagna, COMPLETO)
    totale_donazioni = campagna.donazioni.all().aggregate(importo=Sum('importo'))
    donatori = campagna.donazioni.filter(donatore__isnull=False).distinct('donatore').count()
    contesto = {
        'campagna': campagna,
        'puo_modificare': puo_modificare,
        'totale_donazioni': totale_donazioni['importo'] or 0,
        'totale_donatori': donatori,
    }
    return 'donazioni_campagna_scheda.html', contesto


@pagina_privata
def campagna_fine(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in campagna.responsabili_attuali():  # Se sono responsabile
        redirect(campagna.url)

    contesto = {
        'campagna': campagna,
    }
    return 'donazioni_campagna_fine.html', contesto


@pagina_privata
def campagna_responsabili(request, me, pk):
    campagna = get_object_or_404(Campagna, pk=pk)
    if not me.permessi_almeno(campagna, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    continua_url = campagna.url

    if 'campagna_creata' in request.session and int(request.session['campagna_creata']) == int(pk):
        continua_url = "/donazioni/campagne/%d/fine/" % (int(pk),)
        del request.session['campagna_creata']

    contesto = {
        'delega': RESPONSABILE_CAMPAGNA,
        'campagna': campagna,
        'continua_url': continua_url
    }

    return 'donazioni_campagna_responsabili.html', contesto


# ######## ETICHETTE #################

@pagina_privata
def etichetta(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)

    contesto = {
        'etichetta': etichetta,
        'puo_modificare': me.ha_permesso(GESTIONE_CAMPAGNE),
    }
    return 'donazioni_etichetta_scheda.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def etichetta_nuova(request, me):
    modulo = ModuloEtichetta(request.POST or None)

    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect('donazioni_etichette')

    contesto = {
        'modulo': modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_CAMPAGNE,))
def etichetta_modifica(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)
    if not me.permessi_almeno(etichetta, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    modulo = ModuloEtichetta(request.POST or None, instance=etichetta)
    if modulo.is_valid():
        etichetta = modulo.save()
        return redirect('donazioni_etichette')
    contesto = {
        'modulo': modulo
    }
    return 'donazioni_etichetta_nuova.html', contesto


@pagina_privata
def etichetta_elimina(request, me, pk):
    etichetta = get_object_or_404(Etichetta, pk=pk)
    if not me.permessi_almeno(etichetta, COMPLETO):
        return redirect(ERRORE_PERMESSI)
    etichetta.delete()
    return redirect(reverse('donazioni_etichette'))


@pagina_privata
def etichette_elenco(request, me):
    comitati = me.sedi_attuali().values_list('id', flat=True)
    sedi_deleghe_campagne = me.oggetti_permesso(GESTIONE_CAMPAGNE).values_list('id', flat=True)
    campagne_qs = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    filtro_etichette = Q(comitato__in=chain(comitati, sedi_deleghe_campagne)) | Q(campagne__in=campagne_qs)
    contesto = {
        'etichette': Etichetta.objects.filter(filtro_etichette).distinct(),
        'puo_modificare': me.ha_permessi(GESTIONE_CAMPAGNE)
    }
    return 'donazioni_etichette_elenco.html', contesto


# ############# DONAZIONI e DONATORI ###################

@pagina_privata
def donazione_nuova(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    modulo_donazione = ModuloDonazione(request.POST or None, campagna=campagna_id)
    modulo_donatore = ModuloDonatore(request.POST or None)
    if modulo_donazione.is_valid():
        donazione = modulo_donazione.save(commit=False)
        if modulo_donatore.is_valid():
            donatore = Donatore.nuovo_o_esistente(modulo_donatore.instance)
            donazione.donatore = donatore

        donazione.save()
        return redirect(reverse('donazioni_campagna', args=(campagna_id,)))
    contesto = {
        'modulo_donazione': modulo_donazione,
        'modulo_donatore': modulo_donatore,
        'campagna': campagna,
    }
    return 'donazioni_donazione_nuova.html', contesto


@pagina_privata
def donazioni_elenco(request, me, campagna_id):
    campagna = get_object_or_404(Campagna.objects.prefetch_related('donazioni', 'donazioni__donatore'), pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    totale_donazioni = campagna.donazioni.all().aggregate(importo=Sum('importo'))
    numero_donatori_censiti = campagna.donazioni.filter(donatore__isnull=False).distinct('donatore').count()

    contesto = {
        'campagna': campagna,
        'totale_donazioni': totale_donazioni['importo'],
        'numero_donatori_censiti': numero_donatori_censiti,
    }
    return 'donazioni_campagna_elenco_donazioni.html', contesto


@pagina_privata
def donatori_campagna_elenco(request, me, campagna_id):
    campagna = get_object_or_404(Campagna, pk=campagna_id)
    if not me.permessi_almeno(campagna, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    donatori = Donatore.objects.filter(donazioni__campagna=campagna).annotate(totale_donazioni=Sum('donazioni__importo'))
    contesto = {
        'campagna': campagna,
        'donatori': donatori,
    }
    return 'donatori_elenco.html', contesto


@pagina_privata
def donatori_elenco(request, me):
    campagne = me.oggetti_permesso(GESTIONE_CAMPAGNA)
    donatori = Donatore.objects.filter(donazioni__campagna__in=campagne).annotate(totale_donazioni=Sum('donazioni__importo'))
    contesto = {
        'donatori': donatori,
    }
    return 'donatori_elenco.html', contesto