from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404

from anagrafica.forms import ModuloNuovoProvvedimento, ModuloCreazioneTrasferimento
from anagrafica.models import Appartenenza, Persona, Estensione, ProvvedimentoDisciplinare, Sede
from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI , ERRORE_PERMESSI, MODIFICA
from autenticazione.forms import ModuloCreazioneUtenza
from autenticazione.funzioni import pagina_privata
from base.errori import errore_generico, errore_nessuna_appartenenza
from base.files import Excel, FoglioExcel
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from ufficio_soci.elenchi import ElencoSociAlGiorno, ElencoSostenitori, ElencoVolontari, ElencoOrdinari, \
    ElencoElettoratoAlGiorno, ElencoQuote, ElencoPerTitoli
from ufficio_soci.forms import ModuloCreazioneEstensione, ModuloAggiungiPersona, ModuloReclamaAppartenenza, \
    ModuloReclamaQuota, ModuloReclama
from ufficio_soci.models import Quota, Tesseramento


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us(request, me):
    """
    Ritorna la home page per la gestione dei soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()
    persone = Persona.objects.filter(
        Appartenenza.query_attuale(sede__in=sedi).via("appartenenze")
    )
    attivi = Persona.objects.filter(
        Appartenenza.query_attuale(sede__in=sedi, membro=Appartenenza.VOLONTARIO).via("appartenenze")
    )

    contesto = {
        "sedi": sedi,
        "persone": persone,
        "attivi": attivi,
    }

    return 'us.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_aggiungi(request, me):

    modulo_persona = ModuloAggiungiPersona(request.POST or None)

    if modulo_persona.is_valid():
        persona = modulo_persona.save()
        return redirect("/us/reclama/%d/" % (persona.pk,))

    contesto = {
        "modulo_persona": modulo_persona
    }
    return 'us_aggiungi.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_reclama(request, me):
    """
    Mostra il modulo per reclamare una persona.
    """

    modulo = ModuloReclama(request.POST or None)

    if modulo.is_valid():

        try:
            p = Persona.objects.get(codice_fiscale=modulo.cleaned_data['codice_fiscale'])

            sedi = []
            ss = me.oggetti_permesso(GESTIONE_SOCI)
            for s in ss:  # Per ogni sede di mia competenza
                if p.reclamabile_in_sede(s):  # Posso reclamare?
                    sedi += [s]  # Aggiungi a elenco sedi

            if sedi:
                return redirect("/us/reclama/%d/" % (p.pk,))

            else:
                modulo.add_error('codice_fiscale', "Non puoi reclamare questa persona "
                                                   "in nessuna delle tue Sedi. Potrebbe "
                                                   "essere già appartenente a qualche "
                                                   "Comitato. ")

        except Persona.DoesNotExist:
            modulo.add_error('codice_fiscale', "Nessuna Persona registrata in Gaia "
                                               "con questo codice fiscale.")

    contesto = {
        "modulo": modulo
    }

    return 'us_reclama.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_reclama_persona(request, me, persona_pk):

    persona = get_object_or_404(Persona, pk=persona_pk)

    sedi = []
    ss = me.oggetti_permesso(GESTIONE_SOCI)
    for s in ss:  # Per ogni sede di mia competenza
        if persona.reclamabile_in_sede(s):  # Posso reclamare?
            sedi += [s]  # Aggiungi a elenco sedi

    if not sedi:  # Se non posso reclamarlo in nessuna sede
        return errore_generico(request, me, titolo="Impossibile reclamare appartenenza",
                               messaggio="Questa persona non può essere reclamata in "
                                         "nessuna delle sedi di tua competenza. ",
                               torna_titolo="Torna indietro",
                               torna_url="/us/reclama/")

    sedi_qs = Sede.objects.filter(pk__in=[x.pk for x in sedi])

    modulo_appartenenza = ModuloReclamaAppartenenza(request.POST or None, sedi=sedi_qs, prefix="app")
    modulo_appartenenza.fields['membro'].choices = ((k, v) for k, v in dict(Appartenenza.MEMBRO).items()
                                                    if k in Appartenenza.MEMBRO_RECLAMABILE)
    modulo_quota = ModuloReclamaQuota(request.POST or None, prefix="quota")

    if modulo_appartenenza.is_valid():
        if modulo_quota.is_valid():

            continua = True
            if modulo_quota.cleaned_data['registra_quota'] == modulo_quota.SI:
                if not Tesseramento.aperto_anno(
                    modulo_quota.cleaned_data['data_versamento'].year
                ):
                    modulo_quota.add_error('data_versamento', "Spiacente, non è possibile registrare quote "
                                                              "per l'anno selezionato. ")
                    continua = False

                if modulo_quota.cleaned_data['importo_totale'] <= 1:
                    modulo_quota.add_error('importo_totale', "Importo obbligatorio. Se non vuoi salvare la quota ora, "
                                                             "seleziona 'No' su 'Registra Quota'.")
                    continua = False

            if continua:

                app = modulo_appartenenza.save(commit=False)
                app.persona = persona
                app.save()

                q = modulo_quota.cleaned_data

                if q.get('registra_quota') == modulo_quota.SI:
                    quota = Quota.nuova(
                        appartenenza=app,
                        data_versamento=q.get('data_versamento'),
                        registrato_da=me,
                        importo=q.get('importo_totale'),
                        causale="Iscrizione %s anno %d" % (
                            app.get_membro_display(),
                            q.get('data_versamento').year,
                        )
                    )

                return redirect(persona.url)

    contesto = {
        "modulo_appartenenza": modulo_appartenenza,
        "modulo_quota": modulo_quota,
        "persona": persona,
    }

    return 'us_reclama_persona.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensione(request, me):
    """
    Vista per la creazione di una nuova estensione da ufficio soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()  # es. per controllare che il volontario
                                                         # sia appartente attualmente
                                                         #     ad una delle sedi che gestisco io
    modulo = ModuloCreazioneEstensione(request.POST or None)

    if modulo.is_valid():
        est = modulo.save(commit=False)
        if not est.persona.sede_riferimento():
            return errore_nessuna_appartenenza(request, me)
        if not me.permessi_almeno(est.persona, MODIFICA):
            return redirect(ERRORE_PERMESSI)
        if est.destinazione in est.persona.sedi_attuali():
            modulo.add_error('destinazione', 'Il volontario è già appartenente a questa sede.')
        elif est.destinazione in [x.destinazione for x in me.estensioni_attuali_e_in_attesa()]:
            modulo.add_error('destinazione', 'Il volontario ha già una richiesta di estensione a questa sede.')
        else:
            est.richiedente = me
            est.save()
            est.richiedi()
    contesto = {
        "sedi": sedi,
        "modulo": modulo,
    }

    return 'us_estensione.html', contesto

@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_trasferimento(request, me):
    """
    Vista per la creazione di una nuova estensione da ufficio soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()  # es. per controllare che il volontario sia appartente attualmente
                                                         #     ad una delle sedi che gestisco io

    modulo = ModuloCreazioneTrasferimento(request.POST or None)

    if modulo.is_valid():
        trasf = modulo.save(commit=False)
        if not trasf.persona.sede_riferimento():
            return errore_nessuna_appartenenza(request, me)
        if not me.permessi_almeno(trasf.persona, MODIFICA):
            return redirect(ERRORE_PERMESSI)
        if trasf.destinazione in trasf.persona.sedi_attuali():
            modulo.add_error('destinazione', 'Il volontario è già appartenente a questa sede.')
        elif trasf.destinazione.comitato != trasf.persona.sede_riferimento().comitato and True:##che in realta' e' il discriminatore delle elezioni
            return errore_generico(request, me, messaggio="Non puoi richiedere un trasferimento tra comitati durante il periodo elettorale")
        elif trasf.persona.trasferimento:
            return errore_generico(request, me, messaggio="Il Volontario non può avere piú di una richiesta di trasferimento alla volta")
        else:
            trasf.richiedente = me
            trasf.save()
            trasf.richiedi()
    contesto = {
        "sedi": sedi,
        "modulo": modulo,
    }

    return 'us_estensione.html', contesto

@pagina_privata()
def us_estensioni(request, me):
    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()
    estensioni = Estensione.filter(destinazione__in=(sedi))

    contesto = {
        'estensioni': estensioni,
    }

    return 'us_estensioni.html', contesto

@pagina_privata()
def us_estensione_termina(request, me, pk):
    estensione = get_object_or_404(Estensione, pk=pk)
    if estensione not in me.oggetti_permesso(GESTIONE_SOCI).espandi():
        return redirect(ERRORE_PERMESSI)
    else:
        estensione.termina()
        return redirect('/us/estensioni/')


@pagina_privata()
def us_provvedimento(request, me):

    modulo = ModuloNuovoProvvedimento(request.POST or None)
    if modulo.is_valid():
        modulo.save()
        return redirect("/us/")

    contesto = {
        "modulo": modulo,
    }

    return "us_provvedimento.html", contesto



@pagina_privata
def us_elenco(request, me, elenco_id=None, pagina=1):

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    try:  # Prova a ottenere l'elenco dalla sessione.
        elenco = request.session["elenco_%s" % (elenco_id,)]

    except KeyError:  # Se l'elenco non e' piu' in sessione, potrebbe essere scaduto.
        return errore_generico(request, me, titolo="Sessione scaduta",
                               messaggio="Ricarica la pagina.",
                               torna_url=request.path, torna_titolo="Riprova")

    if elenco.modulo():  # Se l'elenco richiede un modulo

        try:  # Prova a recuperare il modulo riempito
            modulo = elenco.modulo()(request.session["elenco_modulo_%s" % (elenco_id,)])

        except KeyError:  # Se fallisce, il modulo non e' stato ancora compilato
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))

        if not modulo.is_valid():  # Se il modulo non e' valido, qualcosa e' andato storto
            print(request.session["elenco_modulo_%s" % (elenco_id,)])
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))  # Prova nuovamente?

        elenco.modulo_riempito = modulo  # Imposta il modulo

    if request.POST:  # Cambiato il termine di ricerca?
        # Memorizza il nuovo termine
        request.session["elenco_filtra_%s" % (elenco_id,)] = request.POST['filtra']
        # Torna alla prima pagina
        return redirect("/us/elenco/%s/%d/" % (elenco_id, 1))

    # Eventuale termine di ricerca
    filtra = request.session.get("elenco_filtra_%s" % (elenco_id,), default="")

    pagina_precedente = "/us/elenco/%s/%d/" % (elenco_id, pagina-1)
    pagina_successiva = "/us/elenco/%s/%d/" % (elenco_id, pagina+1)
    download_url = "/us/elenco/%s/download/" % (elenco_id,)
    messaggio_url = "/us/elenco/%s/messaggio/" % (elenco_id,)

    risultati = elenco.ordina(elenco.risultati())
    if filtra:  # Se keyword specificata, filtra i risultati
        risultati = elenco.filtra(risultati, filtra)

    p = Paginator(risultati, 15)  # Pagina (num risultati per pagina)
    pg = p.page(pagina)

    contesto = {
        'pagina': pagina,
        'pagine': p.num_pages,
        'totale': p.count,
        'risultati': pg.object_list,
        'ha_precedente': pg.has_previous(),
        'ha_successivo': pg.has_next(),
        'pagina_precedente': pagina_precedente,
        'pagina_successiva': pagina_successiva,
        'elenco_id': elenco_id,
        'download_url': download_url,
        'messaggio_url': messaggio_url,
        'filtra': filtra,
    }

    return elenco.template(), contesto


@pagina_privata
def us_elenco_modulo(request, me, elenco_id):

    try:  # Prova a ottenere l'elenco dalla sessione.
        elenco = request.session["elenco_%s" % (elenco_id,)]

    except KeyError:  # Se l'elenco non e' piu' in sessione, potrebbe essere scaduto.
        raise ValueError("Elenco non presente in sessione.")

    if not elenco.modulo():  # No modulo? Vai all'elenco
        return redirect("/us/elenco/%s/1/" % (elenco_id,))

    modulo = elenco.modulo()(request.POST or None)

    if request.POST and modulo.is_valid():  # Modulo ok
        request.session["elenco_modulo_%s" % (elenco_id,)] = request.POST            # Salva modulo in sessione
        return redirect("/us/elenco/%s/1/" % (elenco_id,))                           # Redirigi alla prima pagina

    contesto = {
        "modulo": modulo
    }

    return 'us_elenchi_inc_modulo.html', contesto


@pagina_privata
def us_elenco_download(request, me, elenco_id):

    try:  # Prova a ottenere l'elenco dalla sessione.
        elenco = request.session["elenco_%s" % (elenco_id,)]

    except KeyError:  # Se l'elenco non e' piu' in sessione, potrebbe essere scaduto.
        raise ValueError("Elenco non presente in sessione.")

    if elenco.modulo():  # Se l'elenco richiede un modulo

        try:  # Prova a recuperare il modulo riempito
            modulo = elenco.modulo()(request.session["elenco_modulo_%s" % (elenco_id,)])

        except KeyError:  # Se fallisce, il modulo non e' stato ancora compilato
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))

        if not modulo.is_valid():  # Se il modulo non e' valido, qualcosa e' andato storto
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))  # Prova nuovamente?

        elenco.modulo_riempito = modulo  # Imposta il modulo

    # Ottiene elenco
    persone = elenco.ordina(elenco.risultati())

    # Crea nuovo excel
    excel = Excel(oggetto=me)

    # Ottiene intestazione e funzioni colonne
    intestazione = [x[0] for x in elenco.excel_colonne()]
    colonne = [x[1] for x in elenco.excel_colonne()]
    fogli = {}

    for persona in persone:
        foglio = elenco.excel_foglio(persona)[:31]
        foglio_key = foglio.lower().strip()
        if foglio_key not in [x.lower() for x in fogli.keys()]:
            fogli.update({
                foglio_key: FoglioExcel(foglio, intestazione)
            })

        persona_colonne = [y if y is not None else "" for y in [x(persona) for x in colonne]]
        fogli[foglio_key].aggiungi_riga(
            *persona_colonne
        )

    excel.fogli = fogli.values()
    excel.genera_e_salva("Elenco.xlsx")

    return redirect(excel.download_url)


@pagina_privata
def us_elenco_messaggio(request, me, elenco_id):

    try:  # Prova a ottenere l'elenco dalla sessione.
        elenco = request.session["elenco_%s" % (elenco_id,)]

    except KeyError:  # Se l'elenco non e' piu' in sessione, potrebbe essere scaduto.
        raise ValueError("Elenco non presente in sessione.")

    if elenco.modulo():  # Se l'elenco richiede un modulo

        try:  # Prova a recuperare il modulo riempito
            modulo = elenco.modulo()(request.session["elenco_modulo_%s" % (elenco_id,)])

        except KeyError:  # Se fallisce, il modulo non e' stato ancora compilato
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))

        if not modulo.is_valid():  # Se il modulo non e' valido, qualcosa e' andato storto
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))  # Prova nuovamente?

        elenco.modulo_riempito = modulo  # Imposta il modulo

    return imposta_destinatari_e_scrivi_messaggio(request, elenco.ordina(elenco.risultati()))


@pagina_privata(permessi=(ELENCHI_SOCI,))
def us_elenchi(request, me, elenco_tipo):

    tipi_elenco = {
        "volontari": (ElencoVolontari, "Elenco dei Volontari"),
        "ordinari": (ElencoOrdinari, "Elenco dei Soci Ordinari"),
        "soci": (ElencoSociAlGiorno, "Elenco dei Soci"),
        "sostenitori": (ElencoSostenitori, "Elenco dei Sostenitori"),
        "elettorato": (ElencoElettoratoAlGiorno, "Elenco Elettorato"),
        "titoli": (ElencoPerTitoli, "Ricerca dei soci per titoli"),
    }

    if elenco_tipo not in tipi_elenco:
        return redirect("/us/")

    elenco_nome = tipi_elenco[elenco_tipo][1]

    if request.POST:  # Ho selezionato delle sedi. Elabora elenco.

        sedi = me.oggetti_permesso(ELENCHI_SOCI).filter(pk__in=request.POST.getlist('sedi'))
        elenco = tipi_elenco[elenco_tipo][0](sedi)

        return 'us_elenco_generico.html', {
            "elenco": elenco,
            "elenco_nome": elenco_nome,
        }

    else:  # Devo selezionare delle Sedi.

        sedi = me.oggetti_permesso(ELENCHI_SOCI)

        return 'us_elenco_sede.html', {
            "sedi": sedi,
            "elenco_nome": elenco_nome,
        }



@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_elenco_soci(request, me):

    elenco = ElencoSociAlGiorno(me.oggetti_permesso(GESTIONE_SOCI))

    contesto = {
        "elenco_nome": "Elenco dei Soci",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_elenco_sostenitori(request, me):

    elenco = ElencoSostenitori(me.oggetti_permesso(GESTIONE_SOCI))

    contesto = {
        "elenco_nome": "Elenco dei Sostenitori",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_elenco_volontari(request, me):

    elenco = ElencoVolontari(me.oggetti_permesso(GESTIONE_SOCI))

    contesto = {
        "elenco_nome": "Elenco dei Volontari Attivi",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_elenco_ordinari(request, me):

    elenco = ElencoOrdinari(me.oggetti_permesso(GESTIONE_SOCI))

    contesto = {
        "elenco_nome": "Elenco dei Soci Ordinari",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_elenco_elettorato(request, me):

    elenco = ElencoElettoratoAlGiorno(me.oggetti_permesso(GESTIONE_SOCI))

    contesto = {
        "elenco_nome": "Elenco Elettorato",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_quote(request, me):

    elenco = ElencoQuote(me.oggetti_permesso(GESTIONE_SOCI))
    contesto = {
        "elenco_nome": "Elenco Quote",
        "elenco": elenco
    }

    return 'us_elenco_generico.html', contesto
