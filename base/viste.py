import json
from datetime import date, timedelta, datetime, time

from django.apps import apps
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model, load_backend, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import SetPasswordForm as ModuloImpostaPassword
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import Context, Template, RequestContext
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.clickjacking import xframe_options_exempt

from jorvik import settings
from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE
from anagrafica.models import Sede, Persona
from anagrafica.permessi.applicazioni import PRESIDENTE, UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA
from anagrafica.permessi.costanti import ERRORE_PERMESSI, GESTIONE_SEDE
from autenticazione.funzioni import pagina_pubblica, pagina_anonima, pagina_privata
from autenticazione.models import Utenza
from formazione.models import PartecipazioneCorsoBase, Aspirante
from posta.models import Messaggio
from .errori import errore_generico, messaggio_generico
from .forms import ModuloRecuperaPassword, ModuloLocalizzatore, ModuloLocalizzatoreItalia
from .forms_extra import ModuloRichiestaSupportoPersone
from .geo import Locazione
from .models import Autorizzazione, Token
from .utils import get_drive_file, rimuovi_scelte
from .classes.autorizzazione import AutorizzazioneProcess


IGNORA_AUTORIZZAZIONI = [
    # ContentType.objects.get_for_model(PartecipazioneCorsoBase).pk
]

ORDINE_ASCENDENTE = 'creazione'
ORDINE_DISCENDENTE = '-creazione'
ORDINE_DEFAULT = ORDINE_DISCENDENTE


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
def browser_supportati(request, me):
    """
    Mostra semplicemente l'elenco dei browser supportati
    """
    return 'base_browser_supportati.html'


@pagina_pubblica
def manutenzione(request, me):
    """
    Mostra semplicemente la pagina di manutenzione ed esce.
    """
    return 'base_manutenzione.html'


@pagina_pubblica
def sessione_scaduta(request, me):
    """
    Mostra un messaggio sul termine forzato della sessione utente.
    """
    contesto = {
        'tempo': settings.TWO_FACTOR_SESSION_DURATA
    }
    return 'base_scaduta.html', contesto


@pagina_anonima
def recupera_password(request):
    """
    Mostra semplicemente la pagina di recupero password.
    """

    def _errore(contesto, modulo, livello=None, delegati=None, email=None, codice_fiscale=None):
        contesto.update({
                'modulo': ModuloRecuperaPassword(),
            })
        if livello:
            contesto.update({'errore': livello})
        if delegati:
            contesto.update({'delegati': delegati})
        if email:
            contesto.update({'email': email})
        if codice_fiscale:
            contesto.update({'codice_fiscale': codice_fiscale})
        return 'base_recupera_password.html', contesto

    contesto = {}
    if request.method == 'POST':
        modulo = ModuloRecuperaPassword(request.POST)
        if modulo.is_valid():

            codice_fiscale = modulo.cleaned_data['codice_fiscale'].upper()
            email = modulo.cleaned_data['email'].lower()
            try:
                per = Persona.objects.get(codice_fiscale=codice_fiscale)
                delegati = per.deleghe_anagrafica()
                if not hasattr(per, 'utenza'):
                    return _errore(contesto, modulo, 2, delegati, email=email, codice_fiscale=codice_fiscale)
                if per.utenza.email != email:
                   return _errore(contesto, modulo, 3, delegati, email=email, codice_fiscale=codice_fiscale)

                Messaggio.costruisci_e_invia(
                    destinatari=[per],
                    oggetto="Nuova password",
                    modello="email_recupero_password.html",
                    corpo={
                        "persona": per,
                        "uid": urlsafe_base64_encode(force_bytes(per.utenza.pk)),
                        "reset_pw_link": default_token_generator.make_token(per.utenza),
                        "scadenza_token": django_settings.PASSWORD_RESET_TIMEOUT_DAYS * 24
                    },
                    utenza=True
                )

                return messaggio_generico(request, None,
                                          titolo="Controlla la tua casella e-mail",
                                          messaggio="Ti abbiamo inviato le istruzioni per cambiare la "
                                                    "tua password tramite e-mail. Controlla la tua "
                                                    "casella al più presto. ",
                                          torna_url="/utente/cambia-password/",
                                          torna_titolo="Accedi e cambia la tua password")

            except Persona.DoesNotExist:
                return _errore(contesto, modulo, 1, email=email, codice_fiscale=codice_fiscale)
    else:
        modulo = ModuloRecuperaPassword()
    contesto.update({
        'modulo': modulo,
    })
    return 'base_recupera_password.html', contesto


@pagina_anonima
def recupera_password_conferma(request, uidb64=None, token=None,
                           template='base_recupero_password_conferma.html',
                           contesto_extra=None):
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        utente = Utenza.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utenza.DoesNotExist):
        utente = None

    if utente is not None and default_token_generator.check_token(utente, token):
        link_valido = True
        titolo = 'Inserisci una nuova password'
        if request.method == 'POST':
            modulo = ModuloImpostaPassword(utente, request.POST)
            if modulo.is_valid():
                modulo.save()
                return HttpResponseRedirect(reverse('recupero_password_completo'))
        else:
            modulo = ModuloImpostaPassword(utente)
    else:
        link_valido = False
        modulo = None
        titolo = 'Errore nell\'impostazione della nuova password'
    contesto = {
        'modulo': modulo,
        'titolo': titolo,
        'link_valido': link_valido,
        "scadenza_token": django_settings.PASSWORD_RESET_TIMEOUT_DAYS * 24
    }
    if contesto_extra is not None:
        contesto.update(contesto_extra)

    return TemplateResponse(request, template, contesto)


def recupero_password_completo(request,
                            template='base_recupero_password_completo.html',
                            contesto_extra=None):
    contesto = {
        'login_url': '/login/',
        'titolo': 'Password reimpostata correttamente',
    }
    if contesto_extra is not None:
        contesto.update(contesto_extra)

    return TemplateResponse(request, template, contesto)


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
    return 'base_informazioni_condizioni.html'


@pagina_pubblica
def informazioni_cookie(request, me):
    """
    Mostra semplicemente la pagina dei cookie.
    """
    return 'base_informazioni_cookie.html'


@pagina_pubblica
def imposta_cookie(request, me):
    """
    Imposta il cookie per nascondere l'informativa cookie.
    """
    pagina_origine = request.META.get('HTTP_REFERER', '/')
    redirect = HttpResponseRedirect(pagina_origine)
    redirect.set_cookie('cookie_approvati', True)
    return redirect


@xframe_options_exempt
@pagina_pubblica(permetti_embed=True)
def informazioni_sedi(request, me):
    """
    Mostra un elenco dei Comitato, su una mappa, ed esce.
    """
    contesto = {
        'sedi': Sede.objects.filter(attiva=True),
        'massimo_lista': REGIONALE,
        'capitale': Sede.objects.filter(attiva=True, nome="Comitato dell'Area Metropolitana di Roma Capitale").first(),
    }
    return 'base_informazioni_sedi.html', contesto


@xframe_options_exempt
@pagina_pubblica(permetti_embed=True)
def informazioni_sede(request, me, slug):
    """Mostra dettagli sul comitato."""
    vicini_km = 15
    sede = get_object_or_404(Sede, slug=slug)
    vicini = sede.vicini(queryset=Sede.objects.filter(attiva=True), km=vicini_km)\
        .exclude(pk__in=sede.unita_sottostanti().values_list('id', flat=True))\
        .exclude(pk=sede.pk)

    context = {
        'sede': sede,
        'vicini': vicini,
        'da_mostrare': vicini | sede.ottieni_discendenti(includimi=True),
        'presidente': sede.presidente(),
        'vice_presidente': sede.vice_presidente(),
        'consiglieri': sede.consiglieri(),
        'consigliere_giovane': sede.consigliere_giovane(),
        'vicini_km': vicini_km,
    }
    return 'base_informazioni_sede.html', context


def pulisci_autorizzazioni(richieste):
    pulite = False
    for richiesta in richieste:
        if richiesta.oggetto is None:
            richiesta.delete()
            pulite = True
    return pulite


@pagina_privata
def autorizzazioni(request, me, content_type_pk=None):
    """ Mostra elenco delle autorizzazioni in attesa. """

    autorizzazioni_in_attesa = me.autorizzazioni().filter(necessaria=True)
    richieste = autorizzazioni_in_attesa.exclude(oggetto_tipo_id__in=IGNORA_AUTORIZZAZIONI)

    richieste_bloccate = dict()
    # richieste_bloccate['corsi'] = PartecipazioneCorsoBase.richieste_non_processabili(richieste)

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
        request.session['autorizzazioni_torna_url'] = "/autorizzazioni/%d/" % int(content_type_pk)

    contesto = {
        "richieste": richieste,
        "richieste_bloccate": richieste_bloccate,
        "sezioni": sezioni,
        "content_type_pk": int(content_type_pk) if content_type_pk else None,
    }

    return 'base_autorizzazioni.html', contesto


@pagina_privata
def autorizzazione_concedi(request, me, pk=None):
    auth = AutorizzazioneProcess(request, me, pk)
    return auth.concedi()


@pagina_privata
def autorizzazione_qualifica_presa_visione(request, me, pk=None):
    auth = AutorizzazioneProcess(request, me, pk)
    return auth.qualifica_presa_visione()


@pagina_privata
def autorizzazione_nega(request, me, pk=None):
    auth = AutorizzazioneProcess(request, me, pk)
    return auth.nega()


@pagina_privata
def autorizzazioni_storico(request, me):
    """
    Mostra storico delle autorizzazioni.
    """

    NUMERO_RICHIESTE = 50

    richieste = me.autorizzazioni().filter(necessaria=False).exclude(oggetto_tipo_id__in=IGNORA_AUTORIZZAZIONI)\
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
    context = dict(show_locazione_block=True)
    app_label, model, pk = request.session['app_label'], \
                           request.session['model'], \
                           int(request.session['pk'])
    oggetto = apps.get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)

    risultati = None
    ricerca = False

    if request.GET.get('italia', False):
        form = ModuloLocalizzatoreItalia(request.POST or None,)
    else:
        form = ModuloLocalizzatore(request.POST or None,)

    if form.is_valid():
        cd = form.cleaned_data
        comune = cd['comune'] if not cd['comune'] else "%s, Province of %s" % (cd['comune'], cd['provincia'])
        stringa = "%s, %s, %s" % (cd['indirizzo'], comune, cd['stato'])
        risultati = Locazione.cerca(stringa)
        ricerca = True

    # Cambia il campo da modificare secondo il modulo richiesto
    locazione_da_cambiare = oggetto.locazione
    if 'modifica_indirizzo_sede' in request.session:
        modifica_indirizzo_sede = request.session['modifica_indirizzo_sede']
        model_field = getattr(oggetto, modifica_indirizzo_sede)

        if modifica_indirizzo_sede == 'sede_operativa':
            locazione_da_cambiare = model_field.all()
            context['show_locazione_block'] = False
        elif modifica_indirizzo_sede == 'indirizzo_per_spedizioni':
            locazione_da_cambiare = model_field

    context.update({
        "locazione": locazione_da_cambiare,
        "continua_url": request.session['continua_url'],
        "modulo": form,
        "ricerca": ricerca,
        "risultati": risultati,
        "oggetto": oggetto,
    })

    if app_label == 'formazione' and model == 'corsobase':
        context['is_corsobase'] = 1  # instead of True

    return 'base_geo_localizzatore.html', context


@pagina_privata
def geo_localizzatore_imposta(request, me):
    session = request.session
    app_label, model, pk = session['app_label'], session['model'], int(session['pk'])

    modifica_indirizzo_sede = None
    if 'modifica_indirizzo_sede' in request.session:
        modifica_indirizzo_sede = request.session['modifica_indirizzo_sede']

    oggetto = apps.get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)
    locazione_aggiunta = oggetto.imposta_locazione(request.POST['indirizzo'],
                                                   modifica_indirizzo_sede)

    if modifica_indirizzo_sede:
        del request.session['modifica_indirizzo_sede']
        request.session['reload_locazione'] = (modifica_indirizzo_sede,
                                               locazione_aggiunta)

    return redirect("/geo/localizzatore/")


@pagina_privata
def pdf(request, me, app_label, model, pk):
    from .classes.pdf import BaseGeneraPDF

    pdf = BaseGeneraPDF(request, me, app_label, model, pk)
    return pdf.make()


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
    from base.forms_extra import ModuloRichiestaSupporto
    modulo = None
    if me:
        deleghe = set([d.tipo for d in me.deleghe_attuali()])
        tipi = set((UFFICIO_SOCI, UFFICIO_SOCI_TEMPORANEO, UFFICIO_SOCI_UNITA, PRESIDENTE))
        if deleghe.intersection(tipi):
            modulo = ModuloRichiestaSupportoPersone(request.POST or None)
        else:
            modulo = ModuloRichiestaSupporto(request.POST or None)

        scelte = modulo.fields['tipo'].choices

        # Solo i delegati possono contattare SECONDO_LIVELLO e TERZO_LIVELLO
        if not me.deleghe_attuali().exists():
            scelte = rimuovi_scelte([modulo.TERZO_LIVELLO, modulo.SECONDO_LIVELLO], scelte)

        modulo.fields['tipo'].choices = scelte

    if modulo and modulo.is_valid():
        tipo = modulo.cleaned_data['tipo']
        oggetto = modulo.cleaned_data['oggetto']
        descrizione = modulo.cleaned_data['descrizione']
        persona = modulo.cleaned_data.get('persona', None)

        oggetto = "(%s) %s" % (tipo, oggetto)
        Messaggio.costruisci_e_invia(
            oggetto=oggetto,
            modello="email_supporto.html",
            mittente=me,
            destinatari=[],
            corpo={
                "testo": descrizione,
                "mittente": me,
                "persona": persona
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


@pagina_privata
def informazioni_statistiche(request, me):

    if not me.utenza.is_staff:
        return redirect(ERRORE_PERMESSI)

    oggi = date.today()

    giorni, etichetta, periodi = 7, 'sett.', 52

    statistiche = []
    aspiranti = {}

    for periodo in range(periodi, -1, -1):

        dati = {}

        fine = oggi - timedelta(days=(giorni * periodo))
        inizio = fine - timedelta(days=giorni - 1)

        fine = datetime.combine(fine, time(23, 59, 59))
        inizio = datetime.combine(inizio, time(0, 0, 0))

        dati['inizio'] = inizio
        dati['fine'] = fine

        # Prima, ottiene tutti i queryset.
        qs_aspiranti = Aspirante.objects.filter(creazione__lte=fine, creazione__gte=inizio)
        num_aspiranti = qs_aspiranti.aggregate(num_aspiranti=Count('id'))['num_aspiranti'] or 0

        # Poi, associa al dizionario statistiche.
        dati['etichetta'] = "%d %s fa" % (periodo, etichetta,)
        dati['registrazioni'] = num_aspiranti

        statistiche.append(dati)

    aspiranti['labels'] = json.dumps([x['etichetta'] for x in statistiche])
    aspiranti['registrazioni'] = json.dumps([x['registrazioni'] for x in statistiche])

    contesto = {'statistiche': {'aspiranti': aspiranti}}
    return 'base_informazioni_statistiche.html', contesto
