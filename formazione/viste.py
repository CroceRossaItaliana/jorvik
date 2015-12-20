from datetime import datetime, timedelta

from django.shortcuts import redirect

from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, GESTIONE_CORSO
from autenticazione.funzioni import pagina_privata
from formazione.forms import ModuloCreazioneCorsoBase
from formazione.models import CorsoBase


@pagina_privata
def formazione(request, me):
    contesto = {
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
        "corsi": me.oggetti_permesso(GESTIONE_CORSO),
    }
    return 'formazione.html', contesto


@pagina_privata
def formazione_corsi_base_elenco(request, me):
    contesto = {
        "corsi": me.oggetti_permesso(GESTIONE_CORSO),
        "puo_pianificare": me.ha_permesso(GESTIONE_CORSI_SEDE),
    }
    return 'formazione_corsi_base_elenco.html', contesto


@pagina_privata
def formazione_corsi_base_domanda(request, me):
    contesto = {
        "sedi": me.oggetti_permesso(GESTIONE_CORSI_SEDE),
    }
    return 'formazione_corsi_base_domanda.html', contesto


@pagina_privata
def formazione_corsi_base_nuovo(request, me):
    modulo = ModuloCreazioneCorsoBase(request.POST or None, initial={"data_inizio":
                                                                     datetime.now() + timedelta(days=14)})

    if modulo.is_valid():
        corso = CorsoBase.nuovo(
            anno=modulo.cleaned_data['data_inizio'].year,
            sede=modulo.cleaned_data['sede'],
            data_inizio=modulo.cleaned_data['data_inizio'],
            data_esame=modulo.cleaned_data['data_inizio'],
        )

        if modulo.cleaned_data['locazione'] == modulo.PRESSO_SEDE:
            corso.locazione = corso.sede.locazione
            corso.save()

        return redirect(corso.url_direttori)

    contesto = {
        "modulo": modulo
    }
    return 'formazione_corsi_base_nuovo.html', contesto


@pagina_privata
def formazione_corsi_base_scheda(request, me, pk):
    pass