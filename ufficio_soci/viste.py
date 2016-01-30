import datetime
import random
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import redirect, get_object_or_404

from anagrafica.forms import ModuloNuovoProvvedimento
from anagrafica.models import Appartenenza, Persona, Estensione, ProvvedimentoDisciplinare, Sede, Dimissione
from anagrafica.permessi.applicazioni import PRESIDENTE
from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI , ERRORE_PERMESSI, MODIFICA
from autenticazione.forms import ModuloCreazioneUtenza
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico, errore_nessuna_appartenenza, messaggio_generico
from base.files import Excel, FoglioExcel
from base.notifiche import NOTIFICA_INVIA
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from ufficio_soci.elenchi import ElencoSociAlGiorno, ElencoSostenitori, ElencoVolontari, ElencoOrdinari, \
    ElencoElettoratoAlGiorno, ElencoQuote, ElencoPerTitoli, ElencoDipendenti, ElencoDimessi, ElencoTrasferiti, \
    ElencoVolontariGiovani, ElencoEstesi, ElencoInRiserva, ElencoIVCM
from ufficio_soci.forms import ModuloCreazioneEstensione, ModuloAggiungiPersona, ModuloReclamaAppartenenza, \
    ModuloReclamaQuota, ModuloReclama, ModuloCreazioneDimissioni, ModuloVerificaTesserino, ModuloElencoRicevute, \
    ModuloCreazioneRiserva, ModuloCreazioneTrasferimento
from ufficio_soci.models import Quota, Tesseramento, Tesserino


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us(request, me):
    """
    Ritorna la home page per la gestione dei soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI)

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



@pagina_privata
def us_dimissioni(request, me, pk):

    modulo = ModuloCreazioneDimissioni(request.POST or None)
    persona = get_object_or_404(Persona, pk=pk)

    if not me.permessi_almeno(persona, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if modulo.is_valid():
        dim = modulo.save(commit=False)
        dim.richiedente = me
        dim.persona = persona
        dim.sede = dim.persona.sede_riferimento()
        dim.appartenenza = persona.appartenenze_attuali().first()
        if modulo.cleaned_data['trasforma_in_sostenitore']:
            app = Appartenenza(precedente=dim.appartenenza, persona=dim.persona, sede=dim.persona.sede_riferimento(),
                               inizio=datetime.date.today(),
                               membro=Appartenenza.SOSTENITORE)
            app.save()
        dim.save()
        dim.applica()
        return messaggio_generico(request, me, titolo="Dimissioni registrate",
                                      messaggio="Le dimissioni sono"
                                                "state registrate con successo",
                                      torna_titolo="Vai allo storico appartenenze",
                                      torna_url=persona.url_profilo_appartenenze)

    contesto = {
        "modulo": modulo,
        "persona": persona,
    }

    return 'us_dimissioni.html', contesto




@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensione(request, me):
    """
    Vista per la creazione di una nuova estensione da ufficio soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI)            # es. per controllare che il volontario
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
            return messaggio_generico(request, me, titolo="Estensione richiesta",
                                      messaggio="L'estensione è stata"
                                                "registrata con successo",
                                      torna_titolo="Registra nuova estensione",
                                      torna_url="/us/estensione/")
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

    sedi = me.oggetti_permesso(GESTIONE_SOCI)            # es. per controllare che il volontario sia appartente attualmente
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
            return errore_generico(request, me, messaggio="Non puoi richiedere un trasferimento tra comitati durante il periodo elettorale", torna_url="/us/trasferimento/")
        elif trasf.persona.trasferimento:
            return errore_generico(request, me, messaggio="Il Volontario non può avere piú di una richiesta di trasferimento alla volta", torna_url="/us/trasferimento/")
        else:
            trasf.richiedente = me
            trasf.save()
            if me.sede_riferimento().comitato == trasf.destinazione.comitato:
                trasf.esegui()
                return messaggio_generico(request, me, titolo="Trasferimento effettuato",
                                      messaggio="Il trasferimento è stato automaticamente effettuato in quanto il "
                                                "la destinazione e' un'unita' territoriale "
                                                "appartenente al suo comitato",
                                      torna_titolo="Richiedi nuovo trasferimento",
                                      torna_url="/us/trasferimento/")
            else:
                trasf.richiedi()

                return messaggio_generico(request, me, titolo="Trasferimento richiesto",
                                      messaggio="Il trasferimento è stato richiesto, ora dovrai accettare la richiesta!",
                                      torna_titolo="Richiedi nuovo trasferimento",
                                      torna_url="/us/trasferimento/")
    contesto = {
        "sedi": sedi,
        "modulo": modulo,
    }

    return 'us_trasferimento.html', contesto

@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensioni(request, me):
    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    estensioni = Estensione.filter(destinazione__in=(sedi))

    contesto = {
        'estensioni': estensioni,
    }

    return 'us_estensioni.html', contesto

@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensione_termina(request, me, pk):
    estensione = get_object_or_404(Estensione, pk=pk)
    if estensione not in me.oggetti_permesso(GESTIONE_SOCI):
        return redirect(ERRORE_PERMESSI)
    else:
        estensione.termina()
        return messaggio_generico(request, me, titolo="Estensione terminata",
                                      messaggio="L'estensione è stata"
                                                "terminata con successo",
                                      torna_titolo="Registra nuova estensione",
                                      torna_url="/us/estensione/")


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_provvedimento(request, me):

    modulo = ModuloNuovoProvvedimento(request.POST or None)
    modulo.fields['sede'].queryset=me.oggetti_permesso(GESTIONE_SOCI)
    if modulo.is_valid():
        if not me.permessi_almeno(modulo.cleaned_data['persona'], MODIFICA):
            modulo.add_error('persona', "Non puoi registrare provvedimenti per questo Volontario!")
        else:
            provvedimento = modulo.save()
            provvedimento.registrato_da = me
            provvedimento.esegui()
            return messaggio_generico(request, me, titolo="Provvedimento inserito",
                                      messaggio="Il provvedimento è stato inserito con successo",
                                      torna_titolo="Inserisci nuovo provvedimento",
                                      torna_url="/us/provvedimento/")

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
    contesto.update(**elenco.kwargs)

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

    FOGLIO_DEFAULT = "Foglio 1"

    fogli_multipli = True
    if 'foglio_singolo' in request.GET:
        fogli_multipli = False

    # Ottiene elenco
    persone = elenco.ordina(elenco.risultati())

    # Crea nuovo excel
    excel = Excel(oggetto=me)

    # Ottiene intestazione e funzioni colonne
    intestazione = [x[0] for x in elenco.excel_colonne()]
    colonne = [x[1] for x in elenco.excel_colonne()]
    if not fogli_multipli:
        intestazione += ["Elenco"]

    fogli = {}

    def __semplifica_nome(nome):
        return nome\
            .replace("/", "")\
            .replace(": ", "-")\
            .replace("Comitato ", "")\
            .replace("Locale ", "")\
            .replace("Provinciale ", "")\
            .replace("Di ", "")\
            .replace("di ", "")\
            .replace("Della ", "")\
            .replace("Dell'", "")\
            .replace("Del ", "")

    for persona in persone:
        foglio = __semplifica_nome(elenco.excel_foglio(persona))[:31] if fogli_multipli else FOGLIO_DEFAULT
        foglio_key = foglio.lower().strip()
        if foglio_key not in [x.lower() for x in fogli.keys()]:
            fogli.update({
                foglio_key: FoglioExcel(foglio, intestazione)
            })

        persona_colonne = [y if y is not None else "" for y in [x(persona) for x in colonne]]
        if not fogli_multipli:
            persona_colonne += [elenco.excel_foglio(persona)]

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

    persone = elenco.ordina(elenco.risultati())
    return imposta_destinatari_e_scrivi_messaggio(request, persone)


@pagina_privata(permessi=(ELENCHI_SOCI,))
def us_elenchi(request, me, elenco_tipo):

    tipi_elenco = {
        "volontari": (ElencoVolontari, "Elenco dei Volontari"),
        "giovani": (ElencoVolontariGiovani, "Elenco dei Volontari Giovani"),
        "ivcm": (ElencoIVCM, "Elenco IV e CM"),
        "dimessi": (ElencoDimessi, "Elenco Dimessi"),
        "riserva": (ElencoInRiserva, "Elenco Volontari in Riserva"),
        "trasferiti": (ElencoTrasferiti, "Elenco Trasferiti"),
        "dipendenti": (ElencoDipendenti, "Elenco dei Dipendenti"),
        "ordinari": (ElencoOrdinari, "Elenco dei Soci Ordinari"),
        "estesi": (ElencoEstesi, "Elenco dei Volontari Estesi/In Estensione"),
        "soci": (ElencoSociAlGiorno, "Elenco dei Soci"),
        "sostenitori": (ElencoSostenitori, "Elenco dei Sostenitori"),
        "elettorato": (ElencoElettoratoAlGiorno, "Elenco Elettorato", "us_elenco_inc_elettorato.html"),
        "titoli": (ElencoPerTitoli, "Ricerca dei soci per titoli"),
    }

    if elenco_tipo not in tipi_elenco:
        return redirect("/us/")

    elenco_nome = tipi_elenco[elenco_tipo][1]
    elenco_template = tipi_elenco[elenco_tipo][2] if len(tipi_elenco[elenco_tipo]) > 2 else None

    if request.POST:  # Ho selezionato delle sedi. Elabora elenco.

        sedi = me.oggetti_permesso(ELENCHI_SOCI).filter(pk__in=request.POST.getlist('sedi'))
        elenco = tipi_elenco[elenco_tipo][0](sedi)

        return 'us_elenco_generico.html', {
            "elenco": elenco,
            "elenco_nome": elenco_nome,
            "elenco_template": elenco_template,
        }

    else:  # Devo selezionare delle Sedi.

        sedi = me.oggetti_permesso(ELENCHI_SOCI)

        return 'us_elenco_sede.html', {
            "sedi": sedi,
            "elenco_nome": elenco_nome,
            "elenco_template": elenco_template,
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
def us_riserva(request, me):
    modulo = ModuloCreazioneRiserva(request.POST or None)

    if modulo.is_valid():
        if not modulo.cleaned_data['persona'].appartenenze_attuali() or not modulo.cleaned_data['persona'].sede_riferimento():
            return errore_generico(titolo="Errore", messaggio="Si è verificato un errore generico.", request=request)
        if not me.permessi_almeno(modulo.cleaned_data['persona'], MODIFICA):
            modulo.add_error('persona', "Non puoi registrare riserve per questo Volontario!")
        else:
            riserva = modulo.save(commit=False)
            riserva.appartenenza = riserva.persona.appartenenze_attuali().first()
            riserva.save()
            riserva.richiedi()
            return messaggio_generico(request, me, titolo="Riserva registrata",
                                      messaggio="La riserva è stato registrata con successo",
                                      torna_titolo="Inserisci nuova riserva",
                                      torna_url="/us/riserva/")

    contesto = {
        "modulo": modulo,
    }

    return "us_riserva.html", contesto

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


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_ricevute(request, me):

    modulo = ModuloElencoRicevute(request.POST or (request.GET or None))

    tipi = [x[0] for x in Quota.TIPO]
    anno = Tesseramento.ultimo_anno()
    if modulo.is_valid():
        tipi = modulo.cleaned_data.get('tipi_ricevute')
        anno = modulo.cleaned_data.get('anno')

    dict_tipi = dict(Quota.TIPO)
    tipi_testo = [dict_tipi[t] for t in tipi]

    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    ricevute = Quota.objects.filter(
        sede__in=sedi,
        anno=anno,
        tipo__in=tipi,
    ).order_by('progressivo')

    non_annullate = ricevute.filter(stato=Quota.REGISTRATA)
    importo = non_annullate.aggregate(Sum('importo'))['importo__sum'] or 0.0
    importo_extra = non_annullate.aggregate(Sum('importo_extra'))['importo_extra__sum'] or 0.0
    importo_totale = importo + importo_extra

    contesto = {
        "modulo": modulo,
        "anno": anno,
        "ricevute": ricevute,
        "tipi_testo": tipi_testo,
        "importo_totale": importo_totale,
    }

    return 'us_ricevute.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_ricevute_annulla(request, me, pk):
    ricevuta = get_object_or_404(Quota, pk=pk)

    if ricevuta.sede not in me.oggetti_permesso(GESTIONE_SOCI):
        return redirect(ERRORE_PERMESSI)

    if ricevuta.stato == ricevuta.REGISTRATA:
        ricevuta.stato = ricevuta.ANNULLATA
        ricevuta.annullato_da = me
        ricevuta.data_annullamento = datetime.date.today()
        ricevuta.save()

    return redirect("/us/ricevute/?anno=%d&tipi_ricevute=%s" % (ricevuta.anno, ricevuta.tipo,))


@pagina_pubblica
def verifica_tesserino(request, me=None):

    modulo = ModuloVerificaTesserino(request.POST or None)
    ricerca = False
    lettera_numero = 0
    lettera = "?"
    tesserino = None
    if modulo.is_valid():
        ricerca = True
        try:
            tesserino = Tesserino.objects.get(codice=modulo.cleaned_data['numero_tessera'])
            cognome = tesserino.persona.cognome
            lettera_numero = random.randint(0, len(cognome))
            lettera = cognome[lettera_numero].upper()
            lettera_numero += 1

        except Tesserino.DoesNotExist:
            tesserino = None

    contesto = {
        "modulo": modulo,
        "tesserino": tesserino,
        "lettera_numero": lettera_numero,
        "lettera": lettera,
        "ricerca": ricerca,
    }
    return 'informazioni_verifica_tesserino.html', contesto
