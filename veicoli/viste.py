from django.shortcuts import get_object_or_404, redirect
from anagrafica.permessi.costanti import GESTIONE_AUTOPARCHI_SEDE, ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from veicoli.forms import ModuloCreazioneVeicolo, ModuloCreazioneAutoparco
from veicoli.models import Veicolo, Autoparco, Collocazione


def _autoparchi_e_veicoli(persona):
    autoparchi = persona.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE)
    veicoli = Veicolo.objects.filter(
        Collocazione.query_attuale().via("collocazioni"),
        collocazioni__sede__in=autoparchi
    )
    return autoparchi, veicoli

@pagina_privata
def veicoli(request, me):
    autoparchi, veicoli = _autoparchi_e_veicoli(me)
    contesto = {
        "veicoli": veicoli,
        "autoparchi": autoparchi,
    }
    return "veicoli_home.html", contesto


@pagina_privata
def veicoli_elenco(request, me):
    autoparchi, veicoli = _autoparchi_e_veicoli(me)
    contesto = {
        "veicoli": veicoli,
        "autoparchi": autoparchi,
    }
    return "veicoli_elenco.html", contesto


@pagina_privata
def veicoli_autoparchi(request, me):
    autoparchi = me.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE)
    contesto = {
        "autoparchi": autoparchi,
    }
    return "veicoli_autoparchi.html", contesto


@pagina_privata
def veicoli_veicolo(request, me, pk):
    veicolo = get_object_or_404(Veicolo, pk=pk)
    contesto = {
        "veicolo": veicolo,
    }
    return "veicoli_veicolo.html", contesto

@pagina_privata
def veicoli_autoparco(request, me, pk):
    autoparco = get_object_or_404(Autoparco, pk=pk)
    contesto = {
        "autoparco": autoparco,
    }
    return "veicoli_autoparco.html", contesto

@pagina_privata
def veicoli_veicolo_modifica_o_nuovo(request, me, pk=None):
    veicolo = None
    if pk is not None:
        veicolo = get_object_or_404(Veicolo, pk=pk)
        if not me.permessi_almeno(MODIFICA, veicolo):
            return redirect(ERRORE_PERMESSI)

    modulo = ModuloCreazioneVeicolo(request.POST or None, instance=veicolo)
    if modulo.is_valid():
        modulo.save()
    return "veicoli_veicolo_nuovo_o_modifica.html"


@pagina_privata
def veicoli_autoparco_modifica_o_nuovo(request, me, pk=None):
    autoparco=None
    if pk is not None:
        autoparco = get_object_or_404(Autoparco, pk=pk)
        if not me.permessi_almeno(MODIFICA, autoparco):
            return redirect(ERRORE_PERMESSI)
    modulo = ModuloCreazioneAutoparco(request.POST or None, instance=autoparco)
    if modulo.is_valid():
        modulo.save()
    return "veicoli_autoparco_nuovo_o_modifica.html"

