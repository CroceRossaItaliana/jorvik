from django.db.models.loading import get_model
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
# Le viste base vanno qui.
from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE
from anagrafica.models import Sede, Persona
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from autenticazione.funzioni import pagina_pubblica, pagina_anonima, pagina_privata
from base import errori
from base.errori import errore_generico
from base.forms import ModuloRecuperaPassword, ModuloMotivoNegazione, ModuloLocalizzatore
from base.geo import Locazione
from base.models import Autorizzazione


@pagina_pubblica
def index(request, me):
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
                per = Persona.objects.get(codice_fiscale=modulo.codice_fiscale, utenza__email=modulo.email)



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
    }
    return 'base_informazioni_sede.html', contesto

@pagina_privata
def autorizzazioni(request, me):
    """
    Mostra elenco delle autorizzazioni in attesa.
    """
    richieste = me.autorizzazioni_in_attesa().order_by('creazione')
    for richiesta in richieste:
        if richiesta.oggetto.autorizzazione_concedi_modulo():
            richiesta.modulo = richiesta.oggetto.autorizzazione_concedi_modulo()

    contesto = {
        "richieste": richieste
    }

    return 'base_autorizzazioni.html', contesto


@pagina_privata
def autorizzazione_concedi(request, me, pk=None):
    """
    Mostra il modulo da compilare per il consenso, ed eventualmente registra l'accettazione.
    """
    richiesta = get_object_or_404(Autorizzazione, pk=pk)

    # Controlla che io possa firmare questa autorizzazione
    if not me.autorizzazioni_in_attesa().filter(pk=richiesta.pk).exists():
        return errore_generico(request, me,
            titolo="Richiesta non trovata",
            messaggio="E' possibile che la richiesta sia stata già approvata o respinta da qualcun altro.",
            torna_titolo="Richieste in attesa",
            torna_url="/autorizzazioni/"
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
            torna_url="/autorizzazioni/"
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
    }

    return 'base_autorizzazioni_nega.html', contesto


@pagina_privata
def autorizzazioni_storico(request, me):
    """
    Mostra storico delle autorizzazioni.
    """
    richieste = me.autorizzazioni_firmate.all().order_by('-ultima_modifica')[0:50]
    contesto = {
        "richieste": richieste
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
        stringa = "%s, %s, %s" % (modulo.cleaned_data['indirizzo'],
                                  modulo.cleaned_data['comune'],
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