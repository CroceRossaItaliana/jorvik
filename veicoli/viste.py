import datetime
from django import forms
from django.shortcuts import get_object_or_404, redirect
from anagrafica.permessi.costanti import GESTIONE_AUTOPARCHI_SEDE, ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from veicoli.forms import ModuloCreazioneVeicolo, ModuloCreazioneAutoparco, ModuloCreazioneManutenzione, \
    ModuloCreazioneFermoTecnico, ModuloCreazioneRifornimento
from veicoli.models import Veicolo, Autoparco, Collocazione, Manutenzione


def _autoparchi_e_veicoli(persona):
    sedi = persona.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE)
    autoparchi = Autoparco.objects.filter(sede__in=sedi)
    veicoli = Veicolo.objects.filter(
        Collocazione.query_attuale().via("collocazioni"),
        collocazioni__autoparco__in=autoparchi
    )
    return autoparchi, veicoli

@pagina_privata
def veicoli(request, me):
    sedi = me.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE)
    autoparchi, veicoli = _autoparchi_e_veicoli(me)

    veicoli_revisione = veicoli.filter(
        manutenzioni__tipo=Manutenzione.REVISIONE,
    )
    ex = []
    for i in veicoli_revisione:
        if i.ultima_revisione < datetime.now() - datetime.timedelta(days=i.intervallo_revisione):
            ex += [i.pk]
    veicoli_revisione = veicoli_revisione.exclude(pk__in=ex)

    veicoli_manutenzione = veicoli.filter(
        manutenzioni__tipo=Manutenzione.MANUTENZIONE,
    )
    ex = []
    for i in veicoli_manutenzione:
        if i.ultima_manutenzione < datetime.now() - datetime.timedelta(days=365):
            ex += [i.pk]
    veicoli_manutenzione = veicoli_manutenzione.exclude(pk__in=ex)

    contesto = {
        "revisione": veicoli_revisione,
        "manutenzione": veicoli_manutenzione,
        "autoparchi": autoparchi,
        "veicoli": veicoli,
        "sedi": sedi,
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
    autoparchi, veicoli = _autoparchi_e_veicoli(me)
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
    if pk is None:
        autoparchi, veicoli =_autoparchi_e_veicoli(me)
        modulo.fields["autoparco"] = forms.ModelChoiceField(queryset=autoparchi)
        modulo.fields["data_collocazione"] = forms.DateField(initial=datetime.date.today())
    if modulo.is_valid():
        v = modulo.save()
        if pk is None:
            collocazione = Collocazione(
                autoparco=modulo.cleaned_data["autoparco"],
                inizio=modulo.cleaned_data["data_collocazione"],
                veicolo=v
            )
            collocazione.save()

        return redirect("/veicoli/")

    contesto = {
        "modulo": modulo,
    }

    return "veicoli_veicolo_modifica_o_nuovo.html", contesto


@pagina_privata
def veicoli_autoparco_modifica_o_nuovo(request, me, pk=None):
    autoparco=None
    if pk is not None:
        autoparco = get_object_or_404(Autoparco, pk=pk)
        if not me.permessi_almeno(MODIFICA, autoparco):
            return redirect(ERRORE_PERMESSI)
    modulo = ModuloCreazioneAutoparco(request.POST or None, instance=autoparco)
    print(me.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE))
    modulo.fields['sede'].choices = me.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE).values_list('id', 'nome')
    if modulo.is_valid():
        modulo.save()
        return redirect("/veicoli/")
    contesto = {
        "modulo": modulo,
    }
    return "veicoli_autoparco_modifica_o_nuovo.html", contesto

@pagina_privata
def veicoli_manutenzione(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    modulo = ModuloCreazioneManutenzione(request.POST)
    if not me.permessi_almeno(MODIFICA, veicolo):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        m = modulo.save()
        m.veicolo = veicolo
        m.save()
        return redirect("/veicoli/")
    return redirect("/veicoli/manutenzioni/")

@pagina_privata
def veicoli_rifornimento(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    modulo = ModuloCreazioneRifornimento(request.POST)
    if not me.permessi_almeno(MODIFICA, veicolo):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        r = modulo.save(commit=False)
        r.veicolo = veicolo
        r.save()
        return redirect("/veicoli/")
    return redirect("/veicoli/rifornimenti/")

@pagina_privata
def veicoli_fermo_tecnico(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    modulo = ModuloCreazioneFermoTecnico(request.POST)
    if not me.permessi_almeno(MODIFICA, veicolo):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        f = modulo.save()
        f.veicolo = veicolo
        f.save()
        return redirect("/veicoli/")
    return redirect("/veicoli/fermo/")

