import datetime
from django import forms
from django.shortcuts import get_object_or_404, redirect
from anagrafica.permessi.costanti import GESTIONE_AUTOPARCHI_SEDE, ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from veicoli.forms import ModuloCreazioneVeicolo, ModuloCreazioneAutoparco, ModuloCreazioneManutenzione, \
    ModuloCreazioneFermoTecnico, ModuloCreazioneRifornimento, ModuloCreazioneCollocazione
from veicoli.models import Veicolo, Autoparco, Collocazione, Manutenzione, FermoTecnico


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
        if i.ultima_revisione().data < datetime.date.today() - datetime.timedelta(days=i.intervallo_revisione):
            ex += [i.pk]
    veicoli_revisione = veicoli_revisione.exclude(pk__in=ex).distinct('pk')

    veicoli_manutenzione = veicoli.filter(
        manutenzioni__tipo=Manutenzione.MANUTENZIONE_ORDINARIA,
    )
    ex = []
    for i in veicoli_manutenzione:
        if i.ultima_manutenzione().data < datetime.date.today() - datetime.timedelta(days=365):
            ex += [i.pk]
    veicoli_manutenzione = veicoli_manutenzione.exclude(pk__in=ex).distinct('pk')

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
        if not me.permessi_almeno(veicolo, MODIFICA):
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
        "veicolo": veicolo,
    }

    return "veicoli_veicolo_modifica_o_nuovo.html", contesto


@pagina_privata
def veicoli_autoparco_modifica_o_nuovo(request, me, pk=None):
    autoparco=None
    if pk is not None:
        autoparco = get_object_or_404(Autoparco, pk=pk)
        if not me.permessi_almeno(autoparco, MODIFICA):
            return redirect(ERRORE_PERMESSI)
    else:
        autoparco = None
    modulo = ModuloCreazioneAutoparco(request.POST or None, instance=autoparco)
    modulo.fields['sede'].choices = me.oggetti_permesso(GESTIONE_AUTOPARCHI_SEDE).values_list('id', 'nome')
    if modulo.is_valid():
        modulo.save()
        return redirect("/veicoli/autoparchi/")
    contesto = {
        "modulo": modulo,
        "autoparco": autoparco,
    }
    return "veicoli_autoparco_modifica_o_nuovo.html", contesto

@pagina_privata
def veicoli_manutenzione(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    manutenzioni = veicolo.manutenzioni.all().order_by("-data")
    modulo = ModuloCreazioneManutenzione(request.POST or None)
    if not me.permessi_almeno(veicolo, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        m = modulo.save(commit=False)
        m.veicolo = veicolo
        m.creato_da = me
        m.save()
    contesto = {
        "modulo": modulo,
        "manutenzioni": manutenzioni,
         "veicolo": veicolo,
    }
    return "veicoli_manutenzione.html", contesto

@pagina_privata
def veicoli_rifornimento(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    rifornimenti = veicolo.rifornimenti.all().order_by("-data")
    modulo = ModuloCreazioneRifornimento(request.POST or None)
    if not me.permessi_almeno(veicolo, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        r = modulo.save(commit=False)
        r.veicolo = veicolo
        r.creato_da = me
        r.save()
    contesto = {
        "modulo": modulo,
        "rifornimenti": rifornimenti,
         "veicolo": veicolo,
    }
    return "veicoli_rifornimento.html",contesto

@pagina_privata
def veicoli_fermo_tecnico(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk=veicolo)
    fermi = veicolo.fermi_tecnici.all().order_by("-creazione")
    modulo = ModuloCreazioneFermoTecnico(request.POST or None)
    if not me.permessi_almeno(veicolo, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        f = modulo.save(commit=False)
        f.inizio = datetime.date.today()
        f.veicolo = veicolo
        f.save()
    contesto = {
        "modulo": modulo,
        "fermi": fermi,
        "veicolo": veicolo,
    }
    return "veicoli_fermo_tecnico.html", contesto

@pagina_privata
def veicoli_termina_fermo_tecnico(request, me, fermo):
    fermo = get_object_or_404(FermoTecnico, pk=fermo)
    if me.permessi_almeno(fermo.veicolo, MODIFICA):
        fermo.termina()
        return redirect("/veicolo/fermi-tecnici/%s/" %(fermo.veicolo.pk,))
    else:
        return redirect(ERRORE_PERMESSI)

@pagina_privata
def veicoli_collocazioni(request, me, veicolo):
    veicolo = get_object_or_404(Veicolo, pk = veicolo)
    collocazioni = veicolo.collocazioni.all().order_by("-data")
    modulo = ModuloCreazioneCollocazione(request.POST or None)
    if not me.permessi_almeno(veicolo, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    if modulo.is_valid():
        veicolo.collocazione().termina()
        c = modulo.save(commit=False)
        c.veicolo = veicolo
        c.creato_da = me
        c.save()
    contesto = {
        "veicolo": veicolo,
        "collocazioni":collocazioni,
        "modulo": modulo,
    }
    return "veicoli_collocazione.html", contesto


