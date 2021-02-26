from datetime import timedelta

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils.timezone import now
from django.shortcuts import render_to_response, redirect, get_object_or_404

from anagrafica.costanti import NAZIONALE, REGIONALE
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_TITOLI
from autenticazione.funzioni import pagina_privata
from base.errori import (errore_nessuna_appartenenza, errore_no_volontario)
from base.models import Autorizzazione
from formazione.constants import FORMAZIONE_ROLES
from formazione.models import CorsoBase
from posta.models import Messaggio

from .forms import (FormAddQualificaCRI, ModuloNuovoTitoloPersonale, ModuloDettagliTitoloPersonale,
                    FormAddAltreQualifica)
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
                query = query.filter(modalita_titoli_cri=Titolo.CORSO_ONLINE)
            elif tipo == CorsoBase.CORSO_NUOVO:
                query = query.filter(modalita_titoli_cri__isnull=True)
            elif tipo == CorsoBase.CORSO_EQUIPOLLENZA:
                query = query.filter(modalita_titoli_cri=Titolo.CORSO_EQUIPOLLENZA)

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
    form_add_altra_qualifica = FormAddAltreQualifica()

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
        "form_add_altra_qualifica": form_add_altra_qualifica,
        "titoli": titoli.order_by('-creazione', '-data_ottenimento', '-data_scadenza'),
        "titolo": titolo_selezionato
    }
    return 'cv_index.html', context


@pagina_privata
def cv_add_qualifica_cri(request, me):
    cv_tc_url = '/utente/curriculum/TC/'
    redirect_url = redirect(cv_tc_url)

    if request.method == 'POST':
        form = FormAddQualificaCRI(request.POST, request.FILES, me=me)
        if form.is_valid():
            cd = form.cleaned_data
            qualifica_created = TitoloPersonale.crea_qualifica_regressa(persona=me, **cd)
            if not qualifica_created:
                messages.error(request, 'Errore.')
                return errore_nessuna_appartenenza(request, me, torna_url=cv_tc_url)

            messages.success(request, "La qualifica è stata inserita.")
            return redirect_url

        messages.success(request, "La qualifica non è stata inserita.")
        return 'cv_add_qualifica_cri.html', {'form': form}

    return redirect_url


@pagina_privata
def cv_add_qualifica_cri(request, me):
    cv_tc_url = '/utente/curriculum/AT/'
    redirect_url = redirect(cv_tc_url)

    if request.method == 'POST':
        form = FormAddAltreQualifica(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            tipo_altro = cd['tipo_altro_titolo']
            if tipo_altro == TitoloPersonale.PARTNERSHIP:
                titolo = Titolo.objects.get(pk=cd['titoli_in_partnership'])
                if cd['no_argomento']:
                    argomento = cd['argomento_nome']
                    argomenti = titolo.argomenti.split(',')
                    argomenti.append(argomento)
                    titolo.argomenti = ','.join(argomenti)
                    titolo.save()
                else:
                    argomento = ','.join(cd['argomento'])

                titolo_personale = TitoloPersonale(
                    persona=me,
                    confermata=True,
                    data_ottenimento=cd['data_ottenimento'],
                    titolo=Titolo.objects.get(pk=cd['titoli_in_partnership']),
                    attestato_file=cd['attestato_file'],
                    argomento=argomento,
                    tipo_altro_titolo=cd['tipo_altro_titolo']
                )
                titolo_personale.save()
            elif tipo_altro == TitoloPersonale.ALTRO:
                no_corso = cd['no_corso']
                if not no_corso:
                    titolo = cd['altri_titolo']
                    if cd['no_argomento']:
                        argomento = cd['argomento_nome']
                        argomenti = titolo.argomenti.split(',')
                        argomenti.append(argomento)
                        titolo.argomenti = ','.join(argomenti)
                        titolo.save()
                    else:
                        argomento = ','.join(cd['argomento'])
                    titolo_personale = TitoloPersonale(
                        persona=me,
                        confermata=True,
                        data_ottenimento=cd['data_ottenimento'],
                        titolo=titolo,
                        attestato_file=cd['attestato_file'],
                        argomento=argomento,
                        tipo_altro_titolo=cd['tipo_altro_titolo']
                    )
                    titolo_personale.save()
                else: # DEVO CREARE IL TITOLO
                    titolo = Titolo(
                        tipo=Titolo.ALTRI_TITOLI,
                        nome=cd['nome_corso'],
                        argomenti=cd['argomento_nome']
                    )
                    titolo.save()
                    titolo_personale = TitoloPersonale(
                        persona=me,
                        confermata=True,
                        data_ottenimento=cd['data_ottenimento'],
                        titolo=titolo,
                        attestato_file=cd['attestato_file'],
                        argomento=cd['argomento_nome'],
                        tipo_altro_titolo=cd['tipo_altro_titolo']
                    )
                    titolo_personale.save()
            else:
                messages.error(request, "La qualifica non è stata inserita correttamente")
                return redirect_url
        else:
            print(form.errors)
            messages.error(request, "La qualifica non è stata inserita correttamente")
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
    richiesta.mail_verifica = True
    richiesta.save()
    volontario = richiesta.richiedente
    vo_sede = volontario.sede_riferimento()

    regionale_sede = vo_sede.superiore(estensione=REGIONALE)

    if vo_sede.estensione == NAZIONALE:
        presidente_regionale = vo_sede.presidente()
        delegati_formazione_regionale = vo_sede.delegati_formazione()
    else:
        vo_sede_regionale = vo_sede.sede_regionale
        presidente_regionale = vo_sede_regionale.presidente()
        delegati_formazione_regionale = vo_sede_regionale.delegati_formazione()

    # Mail settings
    oggetto = "Inserimento errato su GAIA Qualifiche CRI: %s" % volontario.nome_completo

    def _costruisci_e_accoda(destinatario_title: str, destinatari) -> None:

        modello = "email_cv_qualifica_regressa_inserimento_errato"
        if destinatario_title == 'Volontario':
            modello = '%s_al_volontario' % modello

        Messaggio.costruisci_e_accoda(
            oggetto=oggetto,
            modello="%s.html" % modello,
            corpo={
                "volontario": volontario,
                'destinatario': destinatario_title,
                'qualifica': richiesta.oggetto.titolo.nome
            },
            mittente=None,
            destinatari=destinatari,
        )

    _costruisci_e_accoda('Volontario', [volontario])

    Messaggio.invia_raw(
        oggetto="Inserimento su GAIA Qualifiche CRI: %s" % volontario.nome_completo,
        corpo_html=get_template('email_cv_qualifica_regressa_inserimento_errato.html').render(
            {
                "volontario": volontario,
                'qualifica': richiesta.oggetto.titolo.nome,
                'comitato': vo_sede
            },
        ),
        email_mittente=Messaggio.NOREPLY_EMAIL,
        lista_email_destinatari=[TitoloPersonale.MAIL_FORMAZIONE[regionale_sede.pk]],
        allegati=richiesta.oggetto.attestato_file
    )

    messages.success(request, "La notifica è stata inviata a %s" % (TitoloPersonale.MAIL_FORMAZIONE[regionale_sede.pk], ))
    return redirect(reverse('autorizzazioni:aperte'))


def argomenti_corsi_json(request):
    if request.is_ajax:
        id_titolo = request.POST.get('id', None)

        if id_titolo:

            titolo = Titolo.objects.get(pk=id_titolo)

            options_for_select = {argomento: argomento for argomento in titolo.argomenti.split(',')}

            return JsonResponse(options_for_select)

        return JsonResponse({})
