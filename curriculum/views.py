from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404

from anagrafica.permessi.costanti import ERRORE_PERMESSI
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_TITOLI
from autenticazione.funzioni import pagina_privata
from base.errori import (errore_nessuna_appartenenza, errore_no_volontario)
from base.models import Autorizzazione
from formazione.constants import FORMAZIONE_ROLES
from formazione.models import CorsoBase
from posta.models import Messaggio

from .forms import (FormAddQualificaCRI, ModuloNuovoTitoloPersonale, ModuloDettagliTitoloPersonale)
from .models import Titolo, TitoloPersonale


@pagina_privata
def cdf_titolo_json(request, me):
    if request.is_ajax and me.deleghe_attuali(tipo__in=FORMAZIONE_ROLES).exists():
        area_id = request.POST.get('area', None)
        cdf_livello = request.POST.get('cdf_livello', None)
        tipo = request.POST.get('tipo', None)

        if cdf_livello and area_id:
            query = Titolo.objects.filter(is_active=True,
                                          area=area_id[0],
                                          cdf_livello=cdf_livello[0]).exclude(sigla__in=['CRI',])

            if tipo == CorsoBase.CORSO_ONLINE:
                query = query.filter(online=True)
            else:
                query = query.filter(online=False)

            options_for_select = {option['id']: {
                'nome': option['nome'],
                'description': option['description'],
                'prevede_esame': option['scheda_prevede_esame'],
            } for option in query.values('id', 'nome', 'description', 'scheda_prevede_esame')}

            return JsonResponse(options_for_select)

    return JsonResponse({})


@pagina_privata
def curriculum(request, me, tipo=None):
    if not tipo:
        return redirect("/utente/curriculum/CP/")

    if tipo not in dict(Titolo.TIPO):  # Tipo permesso?
        return redirect(ERRORE_PERMESSI)

    if tipo in (Titolo.PATENTE_CRI, Titolo.TITOLO_CRI) and not (me.volontario or me.dipendente):
        return errore_no_volontario(request, me)

    passo = 1
    tipo_display = dict(Titolo.TIPO)[tipo]
    request.session['titoli_tipo'] = tipo
    valida_secondo_form = True
    titolo_selezionato = None

    # Instantiate forms
    form = ModuloNuovoTitoloPersonale(tipo, tipo_display, request.POST or None, me=me)
    form_add_qualifica = FormAddQualificaCRI()

    if form.is_valid():
        cd = form.cleaned_data
        titolo_selezionato = cd['titolo']
        passo = 2
        valida_secondo_form = False

    if 'titolo_selezionato_id' in request.POST:
        titolo_selezionato = Titolo.objects.get(pk=request.POST['titolo_selezionato_id'])
        passo = 2

    if passo == 2:
        form = ModuloDettagliTitoloPersonale(request.POST if request.POST and valida_secondo_form else None)

        if not titolo_selezionato.richiede_data_ottenimento:
            del form.fields['data_ottenimento']

        if not titolo_selezionato.richiede_data_scadenza:
            del form.fields['data_scadenza']

        if not titolo_selezionato.richiede_luogo_ottenimento:
            del form.fields['luogo_ottenimento']

        if not titolo_selezionato.richiede_codice:
            del form.fields['codice']

        if form.is_valid():
            tp = form.save(commit=False)
            tp.persona = me
            tp.titolo = titolo_selezionato
            tp.save()

            if titolo_selezionato.richiede_conferma:
                sede_attuale = me.sede_riferimento()
                if not sede_attuale:
                    tp.delete()
                    return errore_nessuna_appartenenza(request, me, torna_url="/utente/curriculum/%s/" % tipo)

                tp.autorizzazione_richiedi_sede_riferimento(me, INCARICO_GESTIONE_TITOLI)

            return redirect("/utente/curriculum/%s/?inserimento=ok" % tipo)

    titoli = me.titoli_personali.filter(titolo__tipo=tipo)

    context = {
        "tipo": tipo,
        "tipo_display": tipo_display,
        "passo": passo,
        "modulo": form,
        "form_add_qualifica": form_add_qualifica,
        "titoli": titoli.order_by('-creazione', '-data_ottenimento', '-data_scadenza'),
        "titolo": titolo_selezionato
    }
    return 'cv_index.html', context


@pagina_privata
def cv_add_qualifica_cri(request, me):
    redirect_url = redirect('/utente/curriculum/TC/')

    if request.method == 'POST':
        form = FormAddQualificaCRI(request.POST, request.FILES, me=me)
        if form.is_valid():
            cd = form.cleaned_data
            titolo = cd['titolo']
            qualifica_nuova = TitoloPersonale(persona=me, confermata=False, **cd)
            qualifica_nuova.save()

            if titolo.richiede_conferma:
                sede_attuale = me.sede_riferimento()
                if not sede_attuale:
                    qualifica_nuova.delete()
                    return errore_nessuna_appartenenza(request, me, torna_url="/utente/curriculum/TC/")

                qualifica_nuova.richiedi_autorizzazione(qualifica_nuova, me, sede_attuale)

            messages.success(request, "La qualifica è stata inserita.")
            return redirect_url

        return 'cv_add_qualifica_cri.html', {'form': form}

    return redirect_url


@pagina_privata
def cv_cancel(request, me, pk=None):
    titolo = get_object_or_404(TitoloPersonale, pk=pk)
    tipo = titolo.titolo.tipo

    redirect_url = redirect("/utente/curriculum/%s/" % tipo)

    if not titolo.persona == me:
        return redirect(ERRORE_PERMESSI)

    if titolo.qualifica_regresso and titolo.confermata:
        messages.error(request, "Non puoi cancellare la qualifica confermata.")
        return redirect_url

    titolo.delete()

    return redirect_url


@pagina_privata
def cv_qualifica_errata_notifica_comitato_regionale(request, me, pk=None):
    richiesta = Autorizzazione.objects.get(pk=pk)

    volontario = richiesta.richiedente
    presidente = volontario.sede_riferimento().presidente()
    vo_nome_cognome = "%s %s" % (volontario.nome, volontario.cognome)

    Messaggio.costruisci_e_accoda(
        oggetto="Inserimento errato su GAIA Qualifiche CRI: %s" % vo_nome_cognome,
        modello="email_cv_qualifica_regressa_inserimento_errato.html",
        corpo={
            "volontario": volontario,
        },
        mittente=None,
        destinatari=[
            presidente,
            volontario,
        ]
    )
    messages.success(request, "Il presidente %s è stato avvisato." % presidente)
    return redirect(reverse('autorizzazioni:aperte'))
