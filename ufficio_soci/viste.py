from django.core.paginator import Paginator
from django.shortcuts import redirect

from anagrafica.models import Appartenenza, Persona, Estensione
from anagrafica.permessi.costanti import GESTIONE_SOCI, ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata
from base.errori import errore_generico
from base.files import Excel, FoglioExcel
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from ufficio_soci.elenchi import ElencoSociAlGiorno, ElencoSostenitori, ElencoVolontari, ElencoOrdinari, \
    ElencoElettoratoAlGiorno
from ufficio_soci.forms import ModuloCreazioneEstensione


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us(request, me):
    """
    Ritorna la home page per la gestione dei soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()

    contesto = {
        "sedi": sedi,
    }

    return 'us.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_estensione(request, me):
    """
    Vista per la creazione di una nuova estensione da ufficio soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI).espandi()  # es. per controllare che il volontario sia appartente attualmente
                                                         #     ad una delle sedi che gestisco io

    modulo = ModuloCreazioneEstensione(request.POST or None)

    # qui dovrebbe salvare...

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
            modulo = request.session["elenco_modulo_%s" % (elenco_id,)]

        except KeyError:  # Se fallisce, il modulo non e' stato ancora compilato
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))

        if not modulo.is_valid():  # Se il modulo non e' valido, qualcosa e' andato storto
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
        request.session["elenco_modulo_%s" % (elenco_id,)] = modulo     # Salva modulo in sessione
        return redirect("/us/elenco/%s/1/" % (elenco_id,))              # Redirigi alla prima pagina

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
            modulo = request.session["elenco_modulo_%s" % (elenco_id,)]

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
        foglio = elenco.excel_foglio(persona)
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
            modulo = request.session["elenco_modulo_%s" % (elenco_id,)]

        except KeyError:  # Se fallisce, il modulo non e' stato ancora compilato
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))

        if not modulo.is_valid():  # Se il modulo non e' valido, qualcosa e' andato storto
            return redirect("/us/elenco/%s/modulo/" % (elenco_id,))  # Prova nuovamente?

        elenco.modulo_riempito = modulo  # Imposta il modulo

    return imposta_destinatari_e_scrivi_messaggio(request, elenco.ordina(elenco.risultati()))


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
