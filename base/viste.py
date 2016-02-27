import mimetypes
import os

from django.contrib.auth import load_backend, login
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.loading import get_model
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
# Le viste base vanno qui.
from django.views.decorators.cache import cache_page

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE
from anagrafica.models import Sede, Persona
from anagrafica.permessi.costanti import ERRORE_PERMESSI, LETTURA
from autenticazione.funzioni import pagina_pubblica, pagina_anonima, pagina_privata
from autenticazione.models import Utenza
from base import errori
from base.errori import errore_generico, messaggio_generico
from base.forms import ModuloRecuperaPassword, ModuloMotivoNegazione, ModuloLocalizzatore, ModuloRichiestaSupporto
from base.geo import Locazione
from base.models import Autorizzazione, Token
from base.tratti import ConPDF
from base.utils import get_drive_file, rimuovi_scelte
from formazione.models import PartecipazioneCorsoBase
from jorvik import settings
from posta.models import Messaggio


@pagina_pubblica
def index(request, me):

    # Redirect
    if 'p' in request.GET:
        p = request.GET['p']
        if p == 'public.formazione':
            return redirect("/informazioni/formazione/")
        elif p == 'riconoscimento':
            return redirect("/registrati/aspirante/")

    if me:  # Porta utenti identificati a /utente/
        return redirect("/utente/")

    contesto = {
        'numero_comitati': Sede.objects.count(),
    }
    return 'base_home.html', contesto

@pagina_pubblica
def manutenzione(request, me):
    """
    Mostra semplicemente la pagina di manutenzione ed esce.
    """
    return 'base_manutenzione.html'

@pagina_anonima
def recupera_password(request):
    """
    Mostra semplicemente la pagina di recupero password.
    """
    contesto = {}
    if request.method == 'POST':
        modulo = ModuloRecuperaPassword(request.POST)
        if modulo.is_valid():

            try:
                per = Persona.objects.get(codice_fiscale=modulo.cleaned_data['codice_fiscale'].upper(),
                                          utenza__email=modulo.cleaned_data['email'].lower())

                Messaggio.costruisci_e_invia(
                    oggetto="Nuova password",
                    modello=""

                )

                return messaggio_generico(request, None,
                                          titolo="Controlla la tua casella e-mail",
                                          messaggio="Ti abbiamo inviato le istruzioni per cambiare la "
                                                    "tua password tramite e-mail. Controlla la tua "
                                                    "casella al più presto. ",
                                          torna_url="/utente/cambia-password/",
                                          torna_titolo="Accedi e cambia la tua password")

            except Persona.DoesNotExist:
                contesto.update({'errore': True})

    contesto.update({
        'modulo': ModuloRecuperaPassword(),
    })
    return 'base_recupera_password.html', contesto

@pagina_pubblica
def informazioni(request, me):
    """
    Mostra semplicemente la pagina diinformazioni ed esce.
    """
    return 'base_informazioni.html'

@pagina_pubblica
def informazioni_aggiornamenti(request, me):
    """
    Mostra semplicemente la pagina degli aggiornamenti ed esce.
    """
    return 'base_informazioni_aggiornamenti.html'

@pagina_pubblica
def informazioni_sicurezza(request, me):
    """
    Mostra semplicemente la pagina degli aggiornamenti ed esce.
    """
    return 'base_informazioni_sicurezza.html'

@pagina_pubblica
def informazioni_condizioni(request, me):
    """
    Mostra semplicemente la pagina delle condizioni ed esce.
    """
    return 'base_informazioni_condizioni.html'\

@pagina_pubblica
def informazioni_sedi(request, me):
    """
    Mostra un elenco dei Comitato, su una mappa, ed esce.
    """
    contesto = {
        'sedi': Sede.objects.all(),
        'massimo_lista': REGIONALE,
    }
    return 'base_informazioni_sedi.html', contesto

@pagina_pubblica
def informazioni_sede(request, me, slug):
    """
    Mostra dettagli sul comitato.
    """
    sede = get_object_or_404(Sede, slug=slug)
    vicini = sede.vicini(queryset=Sede.objects.all(), km=5)

    contesto = {
        'sede': sede,
        'vicini': vicini,
        'da_mostrare': vicini | sede.ottieni_discendenti(includimi=True),
        'presidente': sede.presidente(),
    }
    return 'base_informazioni_sede.html', contesto


IGNORA_AUTORIZZAZIONI = [
    # ContentType.objects.get_for_model(PartecipazioneCorsoBase).pk
]


def pulisci_autorizzazioni(richieste):
    pulite = False
    for richiesta in richieste:
        if richiesta.oggetto is None:
            richiesta.delete()
            pulite = True
    return pulite


@pagina_privata
def autorizzazioni(request, me, content_type_pk=None):
    """
    Mostra elenco delle autorizzazioni in attesa.
    """

    richieste = me._autorizzazioni_in_attesa().exclude(oggetto_tipo_id__in=IGNORA_AUTORIZZAZIONI)

    ORDINE_ASCENDENTE = 'creazione'
    ORDINE_DISCENDENTE = '-creazione'
    ORDINE_DEFAULT = ORDINE_ASCENDENTE

    if 'ordine' in request.GET:
        if request.GET['ordine'] == 'ASC':
            request.session['autorizzazioni_ordine'] = ORDINE_ASCENDENTE
        else:
            request.session['autorizzazioni_ordine'] = ORDINE_DISCENDENTE
    ordine = request.session.get('autorizzazioni_ordine', default=ORDINE_DEFAULT)

    sezioni = ()  # Ottiene le sezioni
    sezs = richieste.values('oggetto_tipo_id').annotate(Count('oggetto_tipo_id'))

    for sez in sezs:
        modello = ContentType.objects.get(pk=int(sez['oggetto_tipo_id']))
        modello = modello.model_class()
        modello = modello.RICHIESTA_NOME
        sezioni += ((modello, sez['oggetto_tipo_id__count'], int(sez['oggetto_tipo_id'])),)

    richieste = richieste.order_by(ordine, 'id')

    if content_type_pk is not None:
        richieste = richieste.filter(oggetto_tipo_id=int(content_type_pk))

    ricarica = pulisci_autorizzazioni(richieste)

    for richiesta in richieste:

        if richiesta.oggetto.autorizzazione_concedi_modulo():
            richiesta.modulo = richiesta.oggetto.autorizzazione_concedi_modulo()

    if ricarica:  # Ricarica?
        return redirect(request.path)

    request.session['autorizzazioni_torna_url'] = "/autorizzazioni/"
    if sezioni and content_type_pk:
        request.session['autorizzazioni_torna_url'] = "/autorizzazioni/%d/" % (int(content_type_pk),)

    contesto = {
        "richieste": richieste,
        "sezioni": sezioni,
        "content_type_pk": int(content_type_pk) if content_type_pk else None,
    }

    return 'base_autorizzazioni.html', contesto


@pagina_privata
def autorizzazione_concedi(request, me, pk=None):
    """
    Mostra il modulo da compilare per il consenso, ed eventualmente registra l'accettazione.
    """
    richiesta = get_object_or_404(Autorizzazione, pk=pk)

    torna_url = request.session.get('autorizzazioni_torna_url', default="/autorizzazioni/")

    # Controlla che io possa firmare questa autorizzazione
    if not me.autorizzazioni_in_attesa().filter(pk=richiesta.pk).exists():
        return errore_generico(request, me,
            titolo="Richiesta non trovata",
            messaggio="E' possibile che la richiesta sia stata già approvata o respinta da qualcun altro.",
            torna_titolo="Richieste in attesa",
            torna_url=torna_url,
        )

    modulo = None

    # Se la richiesta ha un modulo di consenso
    if richiesta.oggetto.autorizzazione_concedi_modulo():
        if request.POST:
            modulo = richiesta.oggetto.autorizzazione_concedi_modulo()(request.POST)

            if modulo.is_valid():
                # Accetta la richiesta con modulo
                richiesta.concedi(me, modulo=modulo)

        else:
            modulo = richiesta.oggetto.autorizzazione_concedi_modulo()()

    else:
        # Accetta la richiesta senza modulo
        richiesta.concedi(me)

    contesto = {
        "modulo": modulo,
        "richiesta": richiesta,
        "torna_url": torna_url,
    }

    return 'base_autorizzazioni_concedi.html', contesto


@pagina_privata
def autorizzazione_nega(request, me, pk=None):
    """
    Mostra il modulo da compilare per la negazione, ed eventualmente registra la negazione.
    """
    richiesta = get_object_or_404(Autorizzazione, pk=pk)

    # Controlla che io possa firmare questa autorizzazione
    if not me.autorizzazioni_in_attesa().filter(pk=richiesta.pk).exists():
        return errore_generico(request, me,
            titolo="Richiesta non trovata",
            messaggio="E' possibile che la richiesta sia stata già approvata o respinta da qualcun altro.",
            torna_titolo="Richieste in attesa",
            torna_url=request.session['autorizzazioni_torna_url'],
        )

    modulo = None

    # Se la richiesta richiede motivazione
    if richiesta.oggetto.autorizzazione_nega_modulo():
        if request.POST:
            modulo = richiesta.oggetto.autorizzazione_nega_modulo()(request.POST)
            if modulo.is_valid():
                # Accetta la richiesta con modulo
                richiesta.nega(me, modulo=modulo)

        else:
            modulo = richiesta.oggetto.autorizzazione_nega_modulo()()

    else:
        # Nega senza modulo
        richiesta.nega(me)

    contesto = {
        "modulo": modulo,
        "richiesta": richiesta,
        "torna_url": request.session['autorizzazioni_torna_url'],
    }

    return 'base_autorizzazioni_nega.html', contesto


@pagina_privata
def autorizzazioni_storico(request, me):
    """
    Mostra storico delle autorizzazioni.
    """

    NUMERO_RICHIESTE = 50

    richieste = me.autorizzazioni_firmate.all().exclude(oggetto_tipo_id__in=IGNORA_AUTORIZZAZIONI)\
                    .order_by('-ultima_modifica')[0:NUMERO_RICHIESTE]

    ricarica = pulisci_autorizzazioni(richieste)
    if ricarica:
        return redirect("/autorizzazioni/storico/")

    contesto = {
        "richieste": richieste,
        "numero": NUMERO_RICHIESTE,
    }

    return 'base_autorizzazioni_storico.html', contesto


@pagina_privata
def geo_localizzatore(request, me):
    app_label = request.session['app_label']
    model = request.session['model']
    pk = int(request.session['pk'])
    continua_url = request.session['continua_url']
    oggetto = get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)

    risultati = None
    ricerca = False

    modulo = ModuloLocalizzatore(request.POST or None,)
    if modulo.is_valid():
        comune = modulo.cleaned_data['comune'] if not modulo.cleaned_data['comune'] \
                    else "%s, Province of %s" % (modulo.cleaned_data['comune'], modulo.cleaned_data['provincia'])
        stringa = "%s, %s, %s" % (modulo.cleaned_data['indirizzo'],
                                  comune,
                                  modulo.cleaned_data['stato'],)
        risultati = Locazione.cerca(stringa)
        ricerca = True

    contesto = {
        "locazione": oggetto.locazione,
        "continua_url": continua_url,
        "modulo": modulo,
        "ricerca": ricerca,
        "risultati": risultati,
        "oggetto": oggetto,
    }

    return 'base_geo_localizzatore.html', contesto


@pagina_privata
def geo_localizzatore_imposta(request, me):
    app_label = request.session['app_label']
    model = request.session['model']
    pk = int(request.session['pk'])
    oggetto = get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)

    oggetto.imposta_locazione(request.POST['indirizzo'])

    return redirect("/geo/localizzatore/")

@pagina_privata
def pdf(request, me, app_label, model, pk):
    oggetto = get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)
    if not isinstance(oggetto, ConPDF):
        return errore_generico(request, None,
                               messaggio="Impossibile generare un PDF per il tipo specificato.")

    if 'token' in request.GET:
        if not oggetto.token_valida(request.GET['token']):
            return errore_generico(request, me, titolo="Token scaduta",
                                   messaggio="Il link usato è scaduto.")

    elif not me.permessi_almeno(oggetto, LETTURA):
        return redirect(ERRORE_PERMESSI)

    pdf = oggetto.genera_pdf()

    # Se sto scaricando un tesserino, forza lo scaricamento.
    if 'tesserini' in pdf.file.path:
        return pdf_forza_scaricamento(request, pdf)

    return redirect(pdf.download_url)


def pdf_forza_scaricamento(request, pdf):
    """
    Forza lo scaricamento di un file pdf.
    Da usare con cautela, perche' carica il file in memoria
    e blocca il thread fino al completamento della richiesta.
    :param request:
    :param pdf:
    :return:
    """

    percorso_completo = pdf.file.path

    with open(percorso_completo, 'rb') as f:
        data = f.read()

    response = HttpResponse(data, content_type=mimetypes.guess_type(percorso_completo)[0])
    response['Content-Disposition'] = "attachment; filename={0}".format(pdf.nome)
    response['Content-Length'] = os.path.getsize(percorso_completo)
    return response


@pagina_pubblica
def formazione(request, me=None):
    file = "1tRrCVuGJRrMRVQhbMw0-X6s9TeEzvoOqz5zzGm4QgXQ"
    contenuto = get_drive_file(file)
    contesto = {
        "contenuto": contenuto
    }
    return "base_formazione.html", contesto


@pagina_pubblica
def verifica_token(request, me, token):
    verifica = Token.verifica(token, redirect=True)
    if not verifica:
        return errore_generico(request, me, titolo="Token scaduto",
                               messaggio="Potresti aver seguito un link che è scaduto.")

    persona, url = verifica

    user = Utenza.objects.get(persona=persona)
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        login(request, user)
    return redirect(url)


@pagina_pubblica
def supporto(request, me=None):
    modulo = None
    if me:
        modulo = ModuloRichiestaSupporto(request.POST or None)

        if not me.deleghe_attuali().exists():
            scelte = modulo.fields['tipo'].choices
            scelte = rimuovi_scelte([modulo.TERZO_LIVELLO, modulo.SECONDO_LIVELLO], scelte)
            modulo.fields['tipo'].choices = scelte


    if modulo and modulo.is_valid():
        tipo = modulo.cleaned_data['tipo']
        oggetto = modulo.cleaned_data['oggetto']
        descrizione = modulo.cleaned_data['descrizione']

        oggetto = "(%s) %s" % (tipo, oggetto)
        Messaggio.costruisci_e_invia(
            oggetto=oggetto,
            modello="email_supporto.html",
            mittente=me,
            destinatari=[],
            corpo={
                "testo": descrizione,
                "mittente": me,
            },
        )
        return messaggio_generico(request, me, titolo="Richiesta inoltrata",
                                  messaggio="Grazie per aver contattato il supporto. La tua richiesta con "
                                            "oggetto '%s' è stata correttamente inoltrata. Riceverai a minuti "
                                            "un messaggio di conferma del codice ticket assegnato alla "
                                            "tua richiesta." % (oggetto,))

    contesto = {
        "modulo": modulo
    }
    return 'supporto.html', contesto


def redirect_semplice(request, nuovo_url='/'):
    return redirect(nuovo_url)
