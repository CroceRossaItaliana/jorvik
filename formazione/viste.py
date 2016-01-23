from datetime import datetime, timedelta

from django.shortcuts import redirect, get_object_or_404

from anagrafica.permessi.applicazioni import DIRETTORE_CORSO
from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, GESTIONE_CORSO, ERRORE_PERMESSI, COMPLETO, MODIFICA
from autenticazione.funzioni import pagina_privata
from base.errori import ci_siamo_quasi
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
    modulo.fields['sede'].queryset = me.oggetti_permesso(GESTIONE_CORSI_SEDE)

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

        request.session['corso_base_creato'] = corso.pk

        return redirect(corso.url_direttori)

    contesto = {
        "modulo": modulo
    }
    return 'formazione_corsi_base_nuovo.html', contesto


@pagina_privata
def formazione_corsi_base_direttori(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    continua_url = corso.url
    #print("A %s %s" % (request.session['corso_base_creato'], pk,))

    if 'corso_base_creato' in request.session and int(request.session['corso_base_creato']) == int(pk):
        print("B %s %s" % (request.session['corso_base_creato'], pk,))
        continua_url = "/formazione/corsi-base/4/fine/"
        del request.session['corso_base_creato']

    print("Continua a %s" % (continua_url,))

    contesto = {
        "delega": DIRETTORE_CORSO,
        "corso": corso,
        "continua_url": continua_url
    }

    return 'formazione_corsi_base_direttori.html', contesto


@pagina_privata
def formazione_corsi_base_fine(request, me, pk):
    corso = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(corso, COMPLETO):
        return redirect(ERRORE_PERMESSI)

    if me in corso.delegati_attuali():  # Se sono direttore, continuo.
        redirect(corso.url)

    contesto = {
        "corso": corso,
    }
    return 'formazione_corsi_base_fine.html', contesto

@pagina_privata
def aspirante_corso_base_informazioni(request, me, pk):

    if False:
        return ci_siamo_quasi(request, me)

    corso = get_object_or_404(CorsoBase, pk=pk)
    puo_modificare = me.permessi_almeno(corso, MODIFICA)
    contesto = {
        "corso": corso,
        "puo_modificare": puo_modificare
    }
    return 'aspirante_corso_base_scheda_informazioni.html', contesto


@pagina_privata
def aspirante_home(request, me):
    if not hasattr(me, 'aspirante'):
        redirect(ERRORE_PERMESSI)

    contesto = {}
    return 'aspirante_home.html', contesto


@pagina_privata
def aspirante_corsi_base(request, me):
    if not hasattr(me, 'aspirante'):
        redirect(ERRORE_PERMESSI)

    contesto = {
        "corsi": me.aspirante.corsi(),
    }
    return 'aspirante_corsi_base.html', contesto


@pagina_privata
def aspirante_sedi(request, me):
    if not hasattr(me, 'aspirante'):
        redirect(ERRORE_PERMESSI)

    contesto = {
        "sedi": me.aspirante.sedi(),
    }
    return 'aspirante_sedi.html', contesto


@pagina_privata
def aspirante_impostazioni(request, me):
    if not hasattr(me, 'aspirante'):
        redirect(ERRORE_PERMESSI)

    contesto = {}
    return 'aspirante_impostazioni.html', contesto

