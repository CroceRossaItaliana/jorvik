import json
import random
import re
from datetime import datetime
from collections import OrderedDict

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe

from anagrafica.costanti import NAZIONALE, REGIONALE
from anagrafica.forms import ModuloNuovoProvvedimento
from anagrafica.models import Appartenenza, Persona, Estensione, ProvvedimentoDisciplinare, Sede, Dimissione, Riserva, \
    Trasferimento
from anagrafica.permessi.applicazioni import PRESIDENTE
from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI , ERRORE_PERMESSI, MODIFICA, EMISSIONE_TESSERINI
from autenticazione.forms import ModuloCreazioneUtenza
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from base.errori import errore_generico, errore_nessuna_appartenenza, messaggio_generico, messaggio_avvertimento
from base.files import Excel, FoglioExcel
from base.notifiche import NOTIFICA_INVIA
from base.utils import poco_fa, testo_euro, oggi, mezzanotte_24_ieri
from posta.models import Messaggio
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from ufficio_soci.elenchi import ElencoSociAlGiorno, ElencoSostenitori, ElencoVolontari, ElencoOrdinari, \
    ElencoElettoratoAlGiorno, ElencoQuote, ElencoPerTitoli, ElencoDipendenti, ElencoDimessi, ElencoTrasferiti, \
    ElencoVolontariGiovani, ElencoEstesi, ElencoInRiserva, ElencoIVCM, ElencoTesseriniSenzaFototessera, \
    ElencoTesseriniRichiesti, ElencoTesseriniDaRichiedere, ElencoTesseriniRifiutati, ElencoExSostenitori, ElencoSenzaTurni
from ufficio_soci.forms import ModuloCreazioneEstensione, ModuloAggiungiPersona, ModuloReclamaAppartenenza, \
    ModuloReclamaQuota, ModuloReclama, ModuloCreazioneDimissioni, ModuloVerificaTesserino, ModuloElencoRicevute, \
    ModuloCreazioneRiserva, ModuloCreazioneTrasferimento, ModuloQuotaVolontario, ModuloNuovaRicevuta, ModuloFiltraEmissioneTesserini, \
    ModuloLavoraTesserini, ModuloScaricaTesserini, ModuloDimissioniSostenitore
from ufficio_soci.models import Quota, Tesseramento, Tesserino, Riduzione


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us(request, me):
    """
    Ritorna la home page per la gestione dei soci.
    """

    sedi = me.oggetti_permesso(GESTIONE_SOCI)

    persone = Persona.objects.filter(
        Appartenenza.query_attuale(sede__in=sedi).via("appartenenze")
    ).distinct('cognome', 'nome', 'codice_fiscale')
    attivi = Persona.objects.filter(
        Appartenenza.query_attuale(sede__in=sedi, membro=Appartenenza.VOLONTARIO).via("appartenenze")
    ).distinct('cognome', 'nome', 'codice_fiscale')

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

            if p.appartenenze_attuali().filter(membro=Appartenenza.SOSTENITORE).exists():
                messaggio = "Questa persona è già registrata come sostenitore. " \
                            r"Prima di poterla reclamare deve essere dimessa dal ruolo di sostenitore"
            else:
                messaggio = "Non puoi reclamare questa persona in nessuna delle tue Sedi. Potrebbe " \
                            "essere già appartenente a qualche Comitato. "

            if sedi:
                return redirect("/us/reclama/%d/" % (p.pk,))

            else:
                modulo.add_error('codice_fiscale', mark_safe(messaggio))

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
    volontario = False

    sedi = []
    ss = me.oggetti_permesso(GESTIONE_SOCI)
    for s in ss:  # Per ogni sede di mia competenza
        if persona.reclamabile_in_sede(s):  # Posso reclamare?
            sedi += [s]  # Aggiungi a elenco sedi
            volontario = volontario or persona.appartenenze_attuali()\
                .filter(sede=s, membro=Appartenenza.VOLONTARIO).exists()

    if persona.appartenenze_attuali().filter(membro=Appartenenza.SOSTENITORE).exists():
        messaggio_extra = "<br>Questa persona è già registrata come sostenitore. Prima di poterla reclamare deve essere dimessa dal ruolo di sostenitore"
    else:
        messaggio_extra = ""

    if not sedi:  # Se non posso reclamarlo in nessuna sede
        return errore_generico(request, me, titolo="Impossibile reclamare appartenenza",
                               messaggio="Questa persona non può essere reclamata in "
                                         "nessuna delle sedi di tua competenza. " + messaggio_extra,
                               torna_titolo="Torna indietro",
                               torna_url="/us/reclama/")


    questo_anno = poco_fa().year

    tesseramento = Tesseramento.objects.get(anno=questo_anno)

    sedi_qs = Sede.objects.filter(pk__in=[x.pk for x in sedi])

    modulo_appartenenza = ModuloReclamaAppartenenza(request.POST or None, sedi=sedi_qs, prefix="app")
    modulo_appartenenza.fields['membro'].choices = ((k, v) for k, v in dict(Appartenenza.MEMBRO).items()
                                                    if k in Appartenenza.MEMBRO_RECLAMABILE)

    dati_iniziali = {
        "importo": tesseramento.importo_quota_volontario(),
        "riduzione": None
    }
    modulo_quota = ModuloReclamaQuota(request.POST or None, initial=dati_iniziali, sedi=sedi, prefix="quota")

    if modulo_appartenenza.is_valid():
        sede = modulo_appartenenza.cleaned_data.get('sede')
        membro = modulo_appartenenza.cleaned_data.get('membro')
        continua = True
        if not modulo_quota.is_valid() and modulo_quota.get('registra_quota') == modulo_quota.SI:
            continua = False

        appartenenza_ordinario = Appartenenza.query_attuale(persona=persona, membro=Appartenenza.ORDINARIO).first()
        if appartenenza_ordinario:  # Se ordinario presso il regionale.
            if modulo_appartenenza.cleaned_data['inizio'] < appartenenza_ordinario.inizio:
                modulo_appartenenza.add_error('inizio', "La persona non era socio ordinario CRI alla "
                                                        "data selezionata. Inserisci la data corretta di "
                                                        "cambio appartenenza.")
                continua = False
            if membro == Appartenenza.ORDINARIO and not appartenenza_ordinario.appartiene_a(sede=sede):
                modulo_appartenenza.add_error('membro', "La persona e' gia un ordinario "
                                                        "in un altro comitato: %s "
                                              % appartenenza_ordinario.sede.nome_completo)
                continua = False

        appartenenza_dipendente = Appartenenza.query_attuale(persona=persona, membro=Appartenenza.DIPENDENTE).first()
        if appartenenza_dipendente and membro == Appartenenza.DIPENDENTE: # Se dipendente e vuole diventare dipendente
                if appartenenza_dipendente.appartiene_a(sede=sede):
                    modulo_appartenenza.add_error('membro', "La persona e' gia dipendente nel tuo comitato")
                    continua = False
                else:
                    modulo_appartenenza.add_error('membro', "La persona e' gia dipendente "
                                                            "in un altro comitato: %s "
                                                  % appartenenza_dipendente.sede.nome_completo)
                    continua = False

                if modulo_appartenenza.cleaned_data['inizio'] < appartenenza_dipendente.inizio:
                    modulo_appartenenza.add_error('inizio', "La persona non era dipendente alla "
                                                            "data selezionata. Inserisci la data corretta di "
                                                            "cambio appartenenza.")
                    continua = False


        sede = modulo_appartenenza.cleaned_data.get('sede')
        appartenenza_volontario = Appartenenza.query_attuale(persona=persona, membro=Appartenenza.VOLONTARIO).first()
        if appartenenza_volontario:
            if membro == Appartenenza.VOLONTARIO and appartenenza_volontario.appartiene_a(sede=sede):
                modulo_appartenenza.add_error('membro', "La persona e' gia volontario nel tuo comitato")
                continua = False

            if membro == Appartenenza.VOLONTARIO and not appartenenza_volontario.appartiene_a(sede=sede):
                modulo_appartenenza.add_error('membro', "La persona e' gia volontario "
                                                        "in un altro comitato: %s "
                                              % appartenenza_volontario.sede.nome_completo)
                continua = False
        if appartenenza_dipendente:
            if membro == Appartenenza.VOLONTARIO and appartenenza_dipendente.appartiene_a(sede=sede):
                modulo_appartenenza.add_error('membro', "La persona e' gia dipendente nel tuo comitato")
                continua = False

        # Controllo eta' minima socio
        if modulo_appartenenza.cleaned_data.get('membro') in Appartenenza.MEMBRO_SOCIO \
                and persona.eta < Persona.ETA_MINIMA_SOCIO:
            modulo_appartenenza.add_error('membro', "I soci di questo tipo devono avere almeno "
                                                    "%d anni. " % Persona.ETA_MINIMA_SOCIO)
            continua = False

        # Controllo eta' minima socio
        if modulo_appartenenza.cleaned_data.get('membro') in Appartenenza.MEMBRO_SOCIO \
                and persona.eta < Persona.ETA_MINIMA_SOCIO:
            modulo_appartenenza.add_error('membro', "I soci di questo tipo devono avere almeno "
                                                    "%d anni. " % Persona.ETA_MINIMA_SOCIO)
            continua = False

        if continua:
            with transaction.atomic():
                app = modulo_appartenenza.save(commit=False)
                app.persona = persona
                app.save()

                # Termina app. ordinario - I dipendenti rimangono tali
                if appartenenza_ordinario:
                    appartenenza_ordinario.fine = app.inizio
                    appartenenza_ordinario.save()

                # se volontario nello stesso comitato e sta passando a dipendente mette in riserva
                if appartenenza_volontario \
                        and app.membro == app.DIPENDENTE \
                        and (appartenenza_volontario.riserve.exclude(fine__isnull=True).exists() or not appartenenza_volontario.riserve.exclude(fine__isnull=True)) \
                        and appartenenza_volontario.appartiene_a(sede=sede):
                    Riserva.objects.create(inizio=mezzanotte_24_ieri(app.inizio),
                                           persona=persona,
                                           motivo="Adozione come dipendente",
                                           appartenenza=appartenenza_volontario)

                q = modulo_quota.cleaned_data
                riduzione = q.get('riduzione', None)
                registra_quota = q.get('registra_quota')
                importo = q.get('importo')
                data_versamento = q.get('data_versamento')

                if registra_quota == modulo_quota.SI:
                    if riduzione:
                        suffisso = ' - %s' % riduzione.descrizione
                    else:
                        suffisso = ''
                    Quota.nuova(
                        appartenenza=app,
                        data_versamento=data_versamento,
                        registrato_da=me,
                        importo=importo,
                        causale="Iscrizione %s anno %d%s" % (
                            app.get_membro_display(),
                            q.get('data_versamento').year,
                            suffisso,
                        ),
                        tipo=Quota.QUOTA_SOCIO,
                        invia_notifica=True,
                        riduzione=riduzione,
                    )

                return redirect(persona.url)

    contesto = {
        "modulo_appartenenza": modulo_appartenenza,
        "modulo_quota": modulo_quota,
        "persona": persona,
        "volontario": volontario
    }

    return 'us_reclama_persona.html', contesto


@pagina_privata
def us_dimissioni(request, me, pk):

    persona = get_object_or_404(Persona, pk=pk)
    modulo = ModuloCreazioneDimissioni(request.POST or None, pers=persona, me=me)

    if not me.permessi_almeno(persona, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if modulo.is_valid():
        dim = modulo.save(commit=False)
        dim.richiedente = me
        dim.persona = persona
        dim.appartenenza = modulo.cleaned_data['appartenenza']
        dim.sede = dim.appartenenza.sede
        dim.applica(trasforma_in_sostenitore=modulo.cleaned_data['trasforma_in_sostenitore'], applicante=me)

        if dim.motivo == dim.DECEDUTO:
            messaggio = 'Il decesso è stato registrato.<br>Vista la motivazione non sarà inviata alcuna notifica ' \
                        'all\'email del volontario. Sarà cura del Presidente e dell\'Ufficio Soci individuare le ' \
                        'corrette modalità di recupero di tesserino e divisa.'
        else:
            messaggio = "Le dimissioni sono state registrate con successo"

        dim.save()

        if persona.appartenenze_attuali().exclude(id=dim.appartenenza.id).exists():
            presidenti_da_contattare = set()
            for appartenenza_restante in persona.appartenenze_attuali():
                pdc = appartenenza_restante.sede.presidente()
                if not pdc in presidenti_da_contattare:
                    presidenti_da_contattare.add(pdc)

            testo_email = "Le dimissioni di %s sono state registrate con successo, ti invitiamo a  " \
                          "creare nuovamente le deleghe che desideri mantenere attive " % persona.nome_completo

            oggetto = "Riapertura deleghe: %s" % (persona.nome_completo)
            Messaggio.costruisci_e_accoda(
                oggetto=oggetto,
                modello="email_testo.html",
                mittente=me,
                destinatari=presidenti_da_contattare,
                corpo={
                    "testo": testo_email,
                },
            )

            messaggio = "Le dimissioni sono state registrate con successo, <strong>MA</strong> sara' necessario " \
                        "creare nuovamente le deleghe di <strong>%s</strong> nel caso faccia ancora parte " \
                        "del tuo comitato" % persona.nome_completo

            return messaggio_avvertimento(request, me, titolo="Dimissioni registrate",
                                      messaggio=messaggio,
                                      torna_titolo="Vai allo storico appartenenze",
                                      torna_url=persona.url_profilo_appartenenze)
        else:
            return messaggio_generico(request, me, titolo="Dimissioni registrate",
                                      messaggio=messaggio,
                                      torna_titolo="Vai allo storico appartenenze",
                                      torna_url=persona.url_profilo_appartenenze)

    contesto = {
        "modulo": modulo,
        "persona": persona,
    }

    return 'us_dimissioni.html', contesto


@pagina_privata
def us_chiudi_sostenitore(request, me, pk):

    modulo = ModuloDimissioniSostenitore(request.POST or None)
    persona = get_object_or_404(Persona, pk=pk)

    if not me.permessi_almeno(persona, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    if modulo.is_valid():
        dim = modulo.save(commit=False)
        dim.richiedente = me
        dim.persona = persona
        dim.sede = dim.persona.sede_riferimento()
        dim.appartenenza = persona.appartenenze_attuali(membro=Appartenenza.SOSTENITORE).first()
        dim.save()
        dim.applica()

        messaggio = "Le dimissioni sono state registrate con successo"

        return messaggio_generico(request, me, titolo="Dimissioni registrate",
                                  messaggio=messaggio,
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
        if not est.persona.sedi_riferimento().exists():
            return errore_nessuna_appartenenza(request, me)
        if not me.permessi_almeno(est.persona, MODIFICA):
            return redirect(ERRORE_PERMESSI)
        if est.destinazione in est.persona.sedi_attuali():
            modulo.add_error('destinazione', 'Il volontario è già appartenente a questa sede.')
        elif est.destinazione in [x.destinazione for x in est.persona.estensioni_attuali_e_in_attesa()]:
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
        if not trasf.persona.sedi_riferimento().exists():
            return errore_nessuna_appartenenza(request, me)
        if not me.permessi_almeno(trasf.persona, MODIFICA):
            return redirect(ERRORE_PERMESSI)
        if trasf.destinazione in trasf.persona.sedi_attuali():
            modulo.add_error('destinazione', 'Il volontario è già appartenente a questa sede.')
        #elif trasf.destinazione.comitato != trasf.persona.sede_riferimento().comitato and True:##che in realta' e' il discriminatore delle elezioni
        #   return errore_generico(request, me, messaggio="Non puoi richiedere un trasferimento tra comitati durante il periodo elettorale", torna_url="/us/trasferimento/")
        elif trasf.persona.trasferimento:
            return errore_generico(request, me, messaggio="Il Volontario non può avere piú di una richiesta di trasferimento alla volta", torna_url="/us/trasferimento/")
        else:
            trasf.richiedente = me
            trasf.save()
            if me.sede_riferimento().comitato == trasf.destinazione.comitato:
                # trasf.esegui()
                trasf.richiedi()
                Messaggio.costruisci_e_invia(
                    oggetto="Richiesta di trasferimento",
                    modello="email_richiesta_trasferimento_cc.html",
                    corpo={
                        "trasferimento": trasf,
                    },
                    mittente=None,
                    destinatari=[
                        trasf.destinazione.presidente()
                    ]
                )

                return messaggio_generico(request, me, titolo="Trasferimento effettuato",
                                      messaggio="Il trasferimento è stato automaticamente effettuato in quanto il "
                                                "la destinazione e' un'unita' territoriale "
                                                "appartenente al suo comitato",
                                      torna_titolo="Richiedi nuovo trasferimento",
                                      torna_url="/us/trasferimento/")
            else:
                trasf.richiedi()

                Messaggio.costruisci_e_invia(
                    oggetto="Richiesta di trasferimento",
                    modello="email_richiesta_trasferimento_cc.html",
                    corpo={
                        "trasferimento": trasf,
                    },
                    mittente=None,
                    destinatari=[
                        trasf.destinazione.presidente()
                    ]
                )

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
    appartenenza = get_object_or_404(Appartenenza, pk=pk)
    if not me.permessi_almeno(appartenenza.estensione.first(), MODIFICA):
        return redirect(ERRORE_PERMESSI)
    else:
        appartenenza.fine = poco_fa()
        appartenenza.terminazione = Appartenenza.FINE_ESTENSIONE
        appartenenza.save()
        return messaggio_generico(request, me, titolo="Estensione terminata",
                                      messaggio="L'estensione è stata"
                                                "terminata con successo",
                                      torna_titolo="Registra nuova estensione",
                                      torna_url="/us/estensione/")

@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_riserva_termina(request, me, pk):
    riserva = get_object_or_404(Riserva, pk=pk)
    if not me.permessi_almeno(riserva.persona, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    else:
        riserva.termina()
        return messaggio_generico(request, me, titolo="Riserva terminata",
                                      messaggio="La riserva è stata"
                                                "terminata con successo",
                                      torna_titolo="Registra nuova riserva",
                                      torna_url="/us/riserva/")


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
        'elenco': elenco,
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
        "ex-sostenitori": (ElencoExSostenitori, "Elenco degli Ex Sostenitori"),
        "senza-turni": (ElencoSenzaTurni, "Elenco dei volontari con zero turni"),
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
def us_quote_nuova(request, me):

    sedi = me.oggetti_permesso(GESTIONE_SOCI)

    def __is_us_territoriale(me, sedi):
        """
        In Gaia non è prevista la Delega US T su sede LOCALE
        US T su LOCALE gestisce tutte le sedi territoriali al di sotto di essa
        US su LOCALE gestisce tutte le sedi territoriali più la sede locale
        :param me:
        :param sedi:
        :return: ritorna una lista di sedi gestite da un delegato con US o US T
        """
        from anagrafica.permessi.applicazioni import UFFICIO_SOCI_UNITA, UFFICIO_SOCI
        from anagrafica.costanti import LOCALE
        sedi_us_t = []
        sedi_us = []
        espandi = []
        for delega in me.deleghe_attuali():
            # prende le sedi locali su cui è delegato con US T (queste devono essere eliminate)
            if delega.tipo == UFFICIO_SOCI_UNITA and delega.oggetto.estensione == LOCALE:
                sedi_us_t.append(delega.oggetto)
                # se la delega US T è sul locale avra sicuramente potere su le sedi sottostanti
                espandi.extend(delega.oggetto.unita_sottostanti())
            # prende le sedi locali su cui è delegato con US (queste devono essere aggiunte)
            elif delega.tipo == UFFICIO_SOCI and delega.oggetto.estensione == LOCALE:
                sedi_us.append(delega.oggetto)

            sedi_exclude = set(sedi_us_t) - set(sedi_us)
        sedi_tmp = list(sedi.exclude(nome__in=sedi_exclude))
        sedi_tmp.extend(list(Sede.objects.filter(nome__in=[sede.nome for sede in espandi])))
        return sedi_tmp

    sedi = __is_us_territoriale(me, sedi)
    questo_anno = poco_fa().year

    try:
        appena_registrata = Quota.objects.get(pk=request.GET['appena_registrata']) \
            if 'appena_registrata' in request.GET else None
    except Quota.DoesNotExist:
        appena_registrata = None

    try:
        tesseramento = Tesseramento.objects.get(anno=questo_anno)
    except Tesseramento.DoesNotExist:
        tesseramento = None

    if tesseramento:
        dati_iniziali = {
            "importo": tesseramento.importo_quota_volontario(),
            "riduzione": None
        }
        modulo = ModuloQuotaVolontario(request.POST or None,
                                       initial=dati_iniziali, sedi=sedi,
                                       tesseramento=tesseramento)

        if modulo and modulo.is_valid():

            volontario = modulo.cleaned_data['volontario']
            riduzione = modulo.cleaned_data.get('riduzione', None)

            importo = modulo.cleaned_data['importo']
            data_versamento = modulo.cleaned_data['data_versamento']

            appartenenza = volontario.appartenenze_attuali(
                al_giorno=data_versamento, membro=Appartenenza.VOLONTARIO
            ).first()

            comitato = appartenenza.sede.comitato if appartenenza else None

            if not appartenenza:
                modulo.add_error('data_versamento', 'In questa data, il Volontario non risulta appartenente '
                                                    'alla Sede.')

            elif appartenenza.sede not in sedi: # or comitato not in sedi:
                modulo.add_error('volontario', 'Questo Volontario non è appartenente a una Sede di tua competenza.')

            elif not comitato.locazione:
                return errore_generico(request, me, titolo="Necessario impostare indirizzo del Comitato",
                                       messaggio="Per poter rilasciare ricevute, è necessario impostare un indirizzo "
                                                 "per la Sede del Comitato di %s. Il Presidente può gestire i dati "
                                                 "della Sede dalla sezione 'Sedi'." % comitato.nome_completo)

            elif not comitato.codice_fiscale:
                return errore_generico(request, me, titolo="Necessario impostare codice fiscale del Comitato",
                                       messaggio="Per poter rilasciare ricevute, è necessario impostare un "
                                                 "codice fiscale per la Sede del Comitato di %s. Il Presidente può "
                                                 "gestire i dati della Sede dalla sezione 'Sedi'." % comitato.nome_completo)

            else:
                if riduzione:
                    suffisso = ' - %s' % riduzione.descrizione
                else:
                    suffisso = ''
                # OK, paga quota!
                ricevuta = Quota.nuova(
                    appartenenza=appartenenza,
                    data_versamento=data_versamento,
                    registrato_da=me,
                    importo=importo,
                    causale="Rinnovo Quota Associativa %d%s" % (questo_anno, suffisso),
                    tipo=Quota.QUOTA_SOCIO,
                    invia_notifica=True,
                    riduzione=riduzione,
                )
                return redirect("/us/quote/nuova/?appena_registrata=%d" % (ricevuta.pk,))

        ultime_quote = Quota.objects.filter(registrato_da=me, tipo=Quota.QUOTA_SOCIO).order_by('-creazione')[:15]

        importi_possibili = OrderedDict(((Quota.QUOTA_SOCIO, tesseramento.quota_attivo),))
        for riduzione in Riduzione.objects.all():
            importi_possibili[riduzione.pk] = riduzione.quota

        contesto = {
            "importi_possibili": json.dumps(importi_possibili),
            "modulo": modulo,
            "ultime_quote": ultime_quote,
            "anno": questo_anno,
            "appena_registrata": appena_registrata,
        }
    else:
        contesto = {
            "anno": questo_anno,
        }
    return 'us_quote_nuova.html', contesto


@pagina_privata(permessi=(GESTIONE_SOCI,))
def us_ricevute_nuova(request, me):

    sedi = me.oggetti_permesso(GESTIONE_SOCI)

    questo_anno = poco_fa().year

    appena_registrata = Quota.objects.get(pk=request.GET['appena_registrata']) \
        if 'appena_registrata' in request.GET else None

    modulo = ModuloNuovaRicevuta(request.POST or None)
    tesseramento = Tesseramento.ultimo_tesseramento()

    if modulo.is_valid():

        persona = modulo.cleaned_data['persona']
        tipo_ricevuta = modulo.cleaned_data['tipo_ricevuta']
        causale = modulo.cleaned_data['causale']
        importo = modulo.cleaned_data['importo']
        data_versamento = modulo.cleaned_data['data_versamento']

        appartenenza = persona.appartenenze_attuali(al_giorno=data_versamento, sede__in=sedi).first()
        appartenenza_sostenitore = persona.appartenenze_attuali(
            al_giorno=data_versamento, sede__in=sedi, membro=Appartenenza.SOSTENITORE
        ).first()

        comitato = None

        partecipazione_corso = persona.partecipazione_corso_base()

        if partecipazione_corso and partecipazione_corso.corso and partecipazione_corso.corso.sede:
            comitato = partecipazione_corso.corso.sede.comitato

        comitato = appartenenza.sede.comitato if appartenenza else comitato

        if not comitato:
            modulo.add_error('data_versamento', 'In questa data, la persona non risulta appartenente '
                                                'come Volontario o Sostenitore per alla Sede o '
                                                'partecipante confermato ad un corso base attivo.')

        elif tipo_ricevuta == Quota.QUOTA_SOSTENITORE and not appartenenza_sostenitore:
            modulo.add_error('persona', 'Questa persona non è registrata come Sostenitore CRI '
                                        'della Sede. Non è quindi possibile registrare la Ricevuta '
                                        'come Sostenitore CRI.')

        elif not comitato.locazione:
            return errore_generico(request, me, titolo="Necessario impostare indirizzo del Comitato",
                                   messaggio="Per poter rilasciare ricevute, è necessario impostare un indirizzo "
                                             "per la Sede del Comitato di %s. Il Presidente può gestire i dati "
                                             "della Sede dalla sezione 'Sedi'." % comitato.nome_completo)

        elif not comitato.codice_fiscale:
            return errore_generico(request, me, titolo="Necessario impostare codice fiscale del Comitato",
                                   messaggio="Per poter rilasciare ricevute, è necessario impostare un "
                                             "codice fiscale per la Sede del Comitato di %s. Il Presidente può "
                                             "gestire i dati della Sede dalla sezione 'Sedi'." % comitato.nome_completo)

        elif (
                tipo_ricevuta == Quota.QUOTA_SOSTENITORE and
                Quota.objects.filter(
                    persona=persona, sede=comitato, anno=data_versamento.year, tipo=Quota.QUOTA_SOSTENITORE,
                    stato=Quota.REGISTRATA
                ).exists()
        ):
            return errore_generico(
                request, me, titolo="Quota già registrata",
                messaggio="La quota per l'anno %s è già stata registrata per la Sede del Comitato di %s." % (
                    data_versamento.year, comitato.nome_completo
                ))

        else:
            # OK, paga quota!
            ricevuta = Quota.nuova(
                appartenenza=appartenenza,
                corso_comitato=comitato,
                corso_persona=persona,
                data_versamento=data_versamento,
                registrato_da=me,
                importo=importo,
                causale=causale,
                tipo=tipo_ricevuta,
                invia_notifica=True
            )
            return redirect("/us/ricevute/nuova/?appena_registrata=%d" % (ricevuta.pk,))

    ultime_quote = Quota.objects.filter(
        registrato_da=me, tipo__in=[Quota.RICEVUTA, Quota.QUOTA_SOSTENITORE]
    ).order_by('-creazione')[:15]

    contesto = {
        "modulo": modulo,
        "ultime_quote": ultime_quote,
        "anno": questo_anno,
        "appena_registrata": appena_registrata,
        "tesseramento": tesseramento,
    }
    return 'us_ricevute_nuova.html', contesto


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
        Q(Q(sede__in=sedi) | Q(appartenenza__sede__in=sedi)),
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

    if ricevuta.appartenenza.sede not in me.oggetti_permesso(GESTIONE_SOCI):
        return redirect(ERRORE_PERMESSI)

    if ricevuta.stato == ricevuta.REGISTRATA:
        ricevuta.annulla(annullato_da=me, invia_notifica=True)

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
            lettera_numero = random.randint(0, len(cognome) - 1)
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


@pagina_privata
def us_tesserini(request, me):
    return redirect("/us/tesserini/da-richiedere/")


@pagina_privata
def us_tesserini_da_richiedere(request, me):
    """
    Mostra l'elenco dei volontari che hanno i requisiti per la
     richiesta del tesserino ma non hanno una richiesta di tesserino,
     con link per effettuare la richiesta.
    """
    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    elenco = ElencoTesseriniDaRichiedere(sedi)
    contesto = {
        "elenco": elenco
    }
    return "us_tesserini_da_richiedere.html", contesto


@pagina_privata
def us_tesserini_senza_fototessera(request, me):
    """
    Mostra l'elenco dei volontari che non hanno ancora
     una fototessera caricata.
    """
    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    elenco = ElencoTesseriniSenzaFototessera(sedi)
    contesto = {
        "elenco": elenco
    }
    return "us_tesserini_senza_fototessera.html", contesto


@pagina_privata
def us_tesserini_richiesti(request, me):
    """
    Mostra un elenco di tutti i volontari con un tesserino richiesto,
     con un link a maggiori informazioni.
    """
    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    elenco = ElencoTesseriniRichiesti(sedi)
    contesto = {
        "elenco": elenco
    }
    return "us_tesserini_richiesti.html", contesto


@pagina_privata
def us_tesserini_rifiutati(request, me):
    """
    Mostra l'elenco dei volontari per i quali è stata rifiutata la
     richiesta del tesserino.
    """
    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    elenco = ElencoTesseriniRifiutati(sedi)
    contesto = {
        "elenco": elenco
    }
    return "us_tesserini_rifiutati.html", contesto


@pagina_privata
def us_tesserini_richiedi(request, me, persona_pk=None):
    """
    Effettua la richiesta di tesserino per il volontario.
    """
    persona = get_object_or_404(Persona, pk=persona_pk)

    tipo_richiesta = Tesserino.RILASCIO
    duplicato = False

    if not me.permessi_almeno(persona, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    torna = {
        "torna_url": request.GET.get("next", default="/us/tesserini/"),
        "torna_titolo": "Torna indietro",
        "embed": True
    }

    sede = persona.sede_riferimento(membro=Appartenenza.MEMBRO_TESSERINO)
    if not sede:
        return errore_generico(request, me, titolo="La persona non è un volontario",
                               messaggio="È solo possibile richiedere un tesserino per "
                                         "i volontari.", **torna)

    if sede not in me.oggetti_permesso(GESTIONE_SOCI):
        return redirect(ERRORE_PERMESSI)

    if not persona.fototessera_attuale():
        return errore_generico(request, me, titolo="Nessuna fototessera",
                               messaggio="È solo possibile richiedere un tesserino per "
                                         "i volontari in possesso di una fototessera "
                                         "confermata su Gaia.", **torna)

    if persona.tesserini.filter(Q(stato_richiesta__in=(Tesserino.RICHIESTO,)) | Q(codice='')).exists():
        return errore_generico(request, me, titolo="Tesserino non accettato",
                               messaggio="Esiste già una richiesta di un tesserino per la persona "
                                         "e non è pertanto possibile richiedere un duplicato ", **torna)

    tesserini = persona.tesserini.filter(stato_richiesta__in=(Tesserino.RICHIESTO, Tesserino.ACCETTATO))
    if tesserini.exists():
        tipo_richiesta = Tesserino.DUPLICATO
        tesserini.update(valido=False)
        duplicato = True

    comitato = sede.comitato
    if not comitato.locazione:
        return errore_generico(request, me, titolo="Il Comitato non ha un indirizzo",
                               messaggio="La sede di appartenenza del volontario (%s) non ha "
                                         "un indirizzo impostato. Questo è necessario, in quanto "
                                         "viene stampato sul retro del tesserino. Il Presidente "
                                         "può impostare l'indirizzo della Sede dalla sezione "
                                         "'Sedi'." % (comitato,),
                               **torna)

    regionale = comitato.superiore(estensione=REGIONALE)

    if not regionale:
        raise ValueError("%s non ha un comitato regionale." % (comitato,))

    tesserini = []

    if regionale.nome == "Comitato dell'Area Metropolitana di Roma Capitale Coordinamento":
        lazio = Sede.objects.filter(nome="Comitato Regionale Lazio").first()
        # Crea la richiesta di tesserino
        tesserino = Tesserino.objects.create(
            persona=persona,
            emesso_da=lazio,
            tipo_richiesta=tipo_richiesta,
            stato_richiesta=Tesserino.RICHIESTO,
            richiesto_da=me,
        )
        tesserini.append(tesserino)

    # Crea la richiesta di tesserino
    tesserino = Tesserino.objects.create(
        persona=persona,
        emesso_da=regionale,
        tipo_richiesta=tipo_richiesta,
        stato_richiesta=Tesserino.RICHIESTO,
        richiesto_da=me,
    )
    tesserini.append(tesserino)

    if duplicato:
        oggetto = "Richiesta Duplicato Tesserino inoltrata"
    else:
        oggetto = "Richiesta Tesserino inoltrata"

    # Manda l'email al volontario
    Messaggio.costruisci_e_invia(
        oggetto=oggetto,
        modello="posta_richiesta_tesserino.html",
        corpo={
            "persona": persona,
            "tesserino": tesserini[0] if len(tesserini) == 1 else tesserini,
            "is_list": False if len(tesserini) == 1 else True,
            "duplicato": duplicato
        },
        mittente=me,
        destinatari=[persona]
    )

    def __componi_messaggio(tesserini, persona):
        tes = ""
        for tesserino in tesserini:
            tes += "({})".format(tesserino.emesso_da)

        messaggio = "La richiesta di stampa è stata inoltrata correttamente {} {} per il volontario {}".format(
            "alla Sede di" if len(tesserini) == 1 else "alle Sedi di",
            tes,
            persona.nome_completo
        )
        return messaggio

    # Mostra un messaggio
    return messaggio_generico(
        request, me, titolo="Richiesta inoltrata", messaggio=__componi_messaggio(tesserini, persona)
        , **torna)


@pagina_privata
def us_tesserini_emissione(request, me):
    sedi = me.oggetti_permesso(EMISSIONE_TESSERINI)

    sedi = Sede.objects.filter(id__in=sedi.values_list('id', flat=True))

    # Comitati Locali e Provinciali.
    sedi_espandi = sedi.espandi(pubblici=True).comitati().exclude(estensione__in=[NAZIONALE, REGIONALE])

    tesserini = Tesserino.objects.none()

    modulo = ModuloFiltraEmissioneTesserini(request.POST or None, sedi=sedi_espandi)
    modulo_compilato = True if request.POST else False

    if modulo.is_valid():
        stato_emissione = modulo.cleaned_data['stato_emissione']
        sedi_selezionate = modulo.cleaned_data['sedi'].espandi(pubblici=True)
        stato_emissione_q = Q(stato_emissione__in=stato_emissione)
        if '' in stato_emissione:
            stato_emissione_q |= Q(stato_emissione__isnull=True)

        tesserini = Tesserino.objects.filter(
            Q(
                Q(persona__codice_fiscale__icontains=modulo.cleaned_data['cerca']) |
                Q(codice__icontains=modulo.cleaned_data['cerca'])
            ),
            stato_emissione_q,
            emesso_da__in=sedi,
            tipo_richiesta__in=modulo.cleaned_data['tipo_richiesta'],
            stato_richiesta__in=modulo.cleaned_data['stato_richiesta']
        ).order_by(modulo.cleaned_data['ordine'])

        # Ottiene oggetto Q per tutte le appartenenze attuali come Volontario in una delle Sedi selezionate.
        q = Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO, sede__in=sedi_selezionate) \
            .via("persona__appartenenze")
        tesserini = tesserini.filter(q)

    contesto = {
        "tesserini": tesserini,
        "modulo": modulo,
        "modulo_compilato": modulo_compilato
    }
    return "us_tesserini_emissione.html", contesto


@pagina_privata
def us_tesserini_emissione_processa(request, me):

    def __multi_richiesta(sedi):
        """
        Nel caso di Comitato lazio i tesserini richiesti sono sempre 2 (Comitato regionale Lazio e Comitato dell' area metropolitana di roma Coordinamento)
        :return: True se in sedi è presente Comitato lazio o roma
        """
        for sede in sedi:
            if re.search('roma', sede.nome) or re.search('Roma', sede.nome):
                return True
            elif re.search('lazio', sede.nome) or re.search('Lazio', sede.nome):
                return True
        return False

    sedi = me.oggetti_permesso(EMISSIONE_TESSERINI)


    if not request.POST:  # Qui si arriva tramite POST.
        return redirect("/us/tesserini/emissione/")

    if 'tesserini' in request.POST:
        tesserini_pk = [int(x) for x in request.POST.getlist('tesserini')]
        azione = request.POST.get('azione', default='')
        request.session['tesserini'] = tesserini_pk
        request.session['tesserini_azione'] = azione

    else:
        tesserini_pk = request.session.get('tesserini', default=[])
        azione = request.session.get('tesserini_azione', default="scarica")

    assert azione in ['scarica', 'lavora', 'scarica_e_lavora']

    # Ottengo tutti i tesserini
    tesserini = Tesserino.objects.filter(
        pk__in=tesserini_pk, emesso_da__in=sedi
    ).prefetch_related('persona')

    fine = False

    da_lavorare = azione in ['lavora', 'scarica_e_lavora']
    da_scaricare = azione in ['scarica', 'scarica_e_lavora']

    modulo = None

    if not tesserini.exists():
        return errore_generico(request, me, titolo="Nessuna richiesta selezionata",
                               messaggio="Devi selezionare una o più richieste che intendi "
                                         "processare. ",
                               torna_titolo="Indietro", torna_url="/us/tesserini/emissione/")

    if da_lavorare:
        modulo = ModuloLavoraTesserini(request.POST if 'tesserini' not in request.POST else None)
        if modulo.is_valid():

            stato_richiesta = modulo.cleaned_data['stato_richiesta']
            stato_emissione = modulo.cleaned_data['stato_emissione']
            motivo_rifiutato = modulo.cleaned_data['motivo_rifiutato']

            tesserini.update(stato_richiesta=stato_richiesta,
                             stato_emissione=stato_emissione,
                             motivo_rifiutato=motivo_rifiutato,
                             data_conferma=poco_fa())

            if __multi_richiesta(sedi):
                # Devo eliminare richiesta tesserino di Roma Coordinamento
                for tesserino in tesserini:
                    tess = Tesserino.objects.filter(
                        persona=tesserino.persona,
                        emesso_da=Sede.objects.filter(
                            nome="Comitato dell'Area Metropolitana di Roma Capitale Coordinamento"
                        ).first(),
                        stato_richiesta=Tesserino.RICHIESTO
                    )
                    tess.delete()

            # Attiva i tesserini o disattiva come appropriato
            valido = (stato_emissione and stato_richiesta == Tesserino.ACCETTATO)

            # Assicurati che i tesserini abbiano un codice prima di attivarli
            if stato_richiesta == Tesserino.ACCETTATO:
                tesserini_senza_codice = tesserini.filter(Tesserino.query_senza_codice().q)
                for x in tesserini_senza_codice:
                    x.assicura_presenza_codice()

            tesserini.update(valido=valido)

            fine = True

            # invio messaggio all'US richiedente se tesserino rifiutato
            if stato_richiesta == Tesserino.RIFIUTATO:
                for tesserino in tesserini:
                    persona = tesserino.persona
                    Messaggio.costruisci_e_accoda(
                        oggetto="Richiesta tesserino rifiutata",
                        modello="email_tesserino_rifiutato.html",
                        corpo={
                            "mittente": me.nome + " " + me.cognome,
                            "volontario_tesserino_rifiutato": persona.nome + " " + persona.cognome,
                            "motivo_rifiuto": tesserino.motivo_rifiutato,
                        },
                        mittente=me,
                        destinatari=[tesserino.richiesto_da]
                    )

    else:
        modulo = ModuloScaricaTesserini(request.POST if 'tesserini' not in request.POST else None)
        if modulo.is_valid():
            fine = True

    if fine:  # Quando elaborati i tesserini
        if da_scaricare:
            return redirect("/us/tesserini/emissione/scarica/")

        else:
            return messaggio_generico(request, me, titolo="%d tesserini processati" % tesserini.count(),
                                      messaggio="I tesserini sono stati processati con successo.",
                                      torna_titolo="Indietro",
                                      torna_url="/us/tesserini/emissione/")

    contesto = {
        "tesserini": tesserini,
        "modulo": modulo,
        "da_scaricare": da_scaricare,
        "da_lavorare": da_lavorare,
    }
    return "us_tesserini_emissione_processa.html", contesto


@pagina_privata
def us_tesserini_emissione_scarica(request, me):
    sedi = me.oggetti_permesso(EMISSIONE_TESSERINI)
    tesserini_pk = request.session.get('tesserini', default=[])
    tesserini = Tesserino.objects.filter(
        pk__in=tesserini_pk, emesso_da__in=sedi
    ).prefetch_related('persona')

    if not tesserini.exists():
        return redirect("/us/tesserini/emissione/")

    tesserini_link = []
    for tesserino in tesserini:
        tesserini_link += [tesserino.url_pdf_token(me)]

    contesto = {
        "tesserini": tesserini,
        "tesserini_secondi": 3,
        "tesserini_link_json": json.dumps(tesserini_link),
        "tesserini_link": tesserini_link,
    }

    return "us_tesserini_emissione_scarica.html", contesto
