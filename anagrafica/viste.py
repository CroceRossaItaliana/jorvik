import codecs, csv, datetime
from collections import OrderedDict
from importlib import import_module

from django.db.models import Q
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.utils.crypto import get_random_string

from articoli.viste import get_articoli
from autenticazione.funzioni import pagina_anonima, pagina_privata
from autenticazione.models import Utenza
from base.errori import (errore_generico, errore_nessuna_appartenenza,
                         messaggio_generico, errore_no_volontario)
from base.files import Zip
from base.models import Log
from base.stringhe import genera_uuid_casuale
from base.utils import poco_fa, oggi
from curriculum.forms import ModuloNuovoTitoloPersonale, ModuloDettagliTitoloPersonale
from curriculum.models import Titolo, TitoloPersonale
from posta.models import Messaggio
from posta.utils import imposta_destinatari_e_scrivi_messaggio
from sangue.models import Donazione

from .costanti import TERRITORIALE, REGIONALE
from .elenchi import ElencoDelegati
from .utils import _conferma_email, _richiesta_conferma_email
from .permessi.applicazioni import (PRESIDENTE, UFFICIO_SOCI, PERMESSI_NOMI_DICT,
                                    DELEGATO_OBIETTIVO_1, COMMISSARIO, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3,
                                    DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6,
                                    RESPONSABILE_FORMAZIONE,
                                    RESPONSABILE_AUTOPARCO, DELEGATO_CO, UFFICIO_SOCI_UNITA, DELEGHE_RUBRICA, REFERENTE,
                                    RESPONSABILE_AREA, DIRETTORE_CORSO, DELEGATO_AREA, REFERENTE_GRUPPO,
                                    PERMESSI_NOMI, RUBRICHE_TITOLI, CONSIGLIERE, VICE_PRESIDENTE, CONSIGLIERE_GIOVANE,
                                    UFFICIO_SOCI_CM, UFFICIO_SOCI_IIVV)
from .permessi.costanti import (ERRORE_PERMESSI, MODIFICA, LETTURA, GESTIONE_SEDE,
    GESTIONE, ELENCHI_SOCI, GESTIONE_ATTIVITA, GESTIONE_ATTIVITA_AREA, GESTIONE_CORSO)
from .permessi.incarichi import (INCARICO_GESTIONE_RISERVE, INCARICO_GESTIONE_TITOLI,
    INCARICO_GESTIONE_FOTOTESSERE)
from .importa import (VALIDAZIONE_ERRORE, VALIDAZIONE_AVVISO, VALIDAZIONE_OK, import_import_volontari)
from .forms import (ModuloStepComitato, ModuloStepCredenziali, ModuloStepFine,
    ModuloModificaAnagrafica, ModuloModificaAvatar, ModuloCreazioneDocumento,
    ModuloModificaEmailAccesso, ModuloModificaEmailContatto,
    ModuloCreazioneTelefono, ModuloCreazioneEstensione, ModuloCreazioneTrasferimento,
    ModuloCreazioneDelega, ModuloDonatore, ModuloDonazione, ModuloNuovaFototessera,
    ModuloCreazioneRiserva, ModuloModificaPrivacy, ModuloPresidenteSede,
    ModuloImportVolontari, ModuloImportPresidenti, ModuloPulisciEmail,
    ModuloReportFederazione, ModuloStepCodiceFiscale, ModuloStepAnagrafica,
    ModuloPresidenteSedePersonaDiRiferimento, ModuloPresidenteSedeNominativo,)
from .models import (Persona, Documento, Telefono, Estensione, Delega, Trasferimento,
    Appartenenza, Sede, Riserva, Dimissione, Nominativo)


TIPO_VOLONTARIO = 'volontario'
TIPO_ASPIRANTE = 'aspirante'
TIPO_DIPENDENTE = 'dipendente'
TIPO = (TIPO_VOLONTARIO, TIPO_ASPIRANTE, TIPO_DIPENDENTE )

# I vari step delle registrazioni
STEP_COMITATO = 'comitato'
STEP_CODICE_FISCALE = 'codice_fiscale'
STEP_ANAGRAFICA = 'anagrafica'
STEP_CREDENZIALI = 'credenziali'
STEP_FINE = 'fine'
STEP_NOMI = {
    STEP_COMITATO: 'Selezione Comitato',
    STEP_CODICE_FISCALE: 'Codice Fiscale',
    STEP_ANAGRAFICA: 'Dati anagrafici',
    STEP_CREDENZIALI: 'Credenziali',
    STEP_FINE: 'Conferma',
}

# Definisce i vari step di registrazione, in ordine, per ogni tipo di registrazione.
STEP = {
    TIPO_VOLONTARIO: [STEP_COMITATO, STEP_CODICE_FISCALE, STEP_CREDENZIALI, STEP_ANAGRAFICA, STEP_FINE],
    TIPO_ASPIRANTE: [STEP_CODICE_FISCALE, STEP_CREDENZIALI, STEP_ANAGRAFICA, STEP_FINE],
    TIPO_DIPENDENTE: [STEP_COMITATO, STEP_CODICE_FISCALE, STEP_CREDENZIALI, STEP_ANAGRAFICA, STEP_FINE],
}

MODULI = {
    STEP_COMITATO: ModuloStepComitato,
    STEP_CODICE_FISCALE: ModuloStepCodiceFiscale,
    STEP_ANAGRAFICA: ModuloStepAnagrafica,
    STEP_CREDENZIALI: ModuloStepCredenziali,
    STEP_FINE: ModuloStepFine,
}


@pagina_anonima
def registrati(request, tipo, step=None):
    """ La vista per tutti gli step della registrazione. """

    # Controlla che il tipo sia valido (/registrati/<tipo>/)
    if tipo not in TIPO:
        return redirect('/errore/')  # Altrimenti porta ad errore generico

    # Se stiamo leggendo i dati dall'URL per confermare l'email carica anche la sessione
    registration_code = request.GET.get('code', '')
    session_key = request.GET.get('registration', '')

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    uid = None
    if session_key and registration_code:
        featured_session = SessionStore(session_key=session_key)
        uid = featured_session.get('_auth_user_id')
        # Come misura di sicurezza controlliamo di non star impersonando nessuno e cambiamo subito l'id
        # di sessione
        if uid is None and registration_code == featured_session.get('registrazione_id'):
            request.session = featured_session
        request.session.cycle_key()

    # Se nessuno step, assume il primo step per il tipo
    # es. /registrati/volontario/ => /registrati/volontario/comitato/
    if not step:
        step = STEP[tipo][0]
        # Ricomincia, quindi svuoto la sessione!
        request.session['registrati'] = {}

    try:
        sessione = request.session['registrati'].copy()
    except KeyError:
        sessione = {}

    lista_step = [
        # Per ogni step:
        #  nome: Il nome completo dello step (es. "Selezione Comitato")
        #  slug: Il nome per il link (es. "comitato" per /registrati/<tipo>/comitato/")
        #  completato: True se lo step e' stato completato o False se futuro o attuale

        {'nome': STEP_NOMI[x],
         'slug': x,
         'completato': (STEP[tipo].index(x) < STEP[tipo].index(step)),
         'attuale': (STEP[tipo].index(x) == STEP[tipo].index(step)),
         'modulo': MODULI[x](initial=sessione) if MODULI[x] else None,} for x in STEP[tipo]
    ]

    # Controlla se e' l'ultimo step
    if STEP[tipo].index(step) == len(STEP[tipo]) - 1:
        step_successivo = None
    else:
        step_successivo = STEP[tipo][STEP[tipo].index(step) + 1]

    step_modulo = MODULI[step]

    # Se questa e' la ricezione dello step compilato
    if request.method == 'POST':
        modulo = step_modulo(request.POST)
        if modulo.is_valid():

            # TODO MEMORIZZA

            for k in modulo.data:
                sessione[k] = modulo.data[k]
            request.session['registrati'] = sessione

            return redirect("/registrati/%s/%s/" % (tipo, step_successivo,))

    else:
        if step_modulo:
            modulo = step_modulo(initial=sessione)
        else:
            modulo = None

    context = {
        'email': sessione.get('email'),
        'attuale_nome': STEP_NOMI[step],
        'attuale_slug': step,
        'lista_step': lista_step,
        'step_successivo': step_successivo,
        'tipo': tipo,
        'modulo': modulo,
    }

    if step == STEP_ANAGRAFICA:

        if 'registrazione_id' not in request.session:
            request.session['registrazione_id'] = get_random_string(length=32)

        if not sessione.get('email'):
            context = {
                'attuale_nome': STEP_NOMI[step],
                'attuale_slug': step,
                'lista_step': lista_step,
                'tipo': tipo,
            }
            return 'anagrafica_registrati_errore.html', context

        else:
            if uid is not None or request.session['registrazione_id'] != registration_code:
                email_body = {
                    'tipo': tipo,
                    'step': step,
                    'code': request.session['registrazione_id'],
                    'email': sessione.get('email'),
                    'sessione': request.session.session_key
                }

                Messaggio.invia_raw(
                   oggetto="Registrazione su Gaia",
                   corpo_html=get_template('email_conferma.html').render(email_body),
                   email_mittente=None,
                   lista_email_destinatari=[
                        sessione.get('email')
                   ]
                )
                link_debug = '/registrati/{tipo}/{step}/?code={code}&registration={sessione}'.format(
                    tipo=tipo, step=step, code=request.session['registrazione_id'],
                    sessione=request.session.session_key
                )

                context = {
                    'attuale_nome': STEP_NOMI[step],
                    'attuale_slug': step,
                    'lista_step': lista_step,
                    'email': sessione.get('email'),
                    'tipo': tipo,
                    'link_debug': link_debug if settings.DEBUG else ''
                }
                return 'anagrafica_registrati_attesa_mail.html', context

    return 'anagrafica_registrati_step_%s.html' % step, context


@pagina_anonima
def registrati_conferma(request, tipo):
    """
    Controlla che tutti i parametri siano corretti in sessione ed effettua
    la registrazione vera e propria!
    """

    # Controlla che il tipo sia valido (/registrati/<tipo>/)
    if tipo not in TIPO:
        return redirect('/errore/')  # Altrimenti porta ad errore generico

    dati = {}

    try:
        sessione = request.session['registrati'].copy()
    except KeyError:
        sessione = {}

    form_confirm = ModuloStepFine(request.POST)

    # Carica tutti i moduli inviati da questo tipo di registrazione
    for (k, form) in [(x, MODULI[x](data=sessione)) for x in STEP[tipo] if MODULI[x] is not None]:
        if k == STEP_FINE:
            """ Comportamento adeguato per la form ModuloStepFine introdotta 
                dall'issue GAIA-49, altrimenti finiva nell'exception sotto. """
            if form_confirm.is_valid():
                dati.update(form_confirm.cleaned_data)
            else:
                response = redirect('/registrati/aspirante/fine/')
                messages.error(request, 'Controlla tutti i campo obbligatori.')
                return response
            continue

        # Controlla nuovamente la validita'
        if not form.is_valid():
            raise ValueError("Errore nella validazione del sub-modulo %s" % k)

        # Aggiunge tutto a "dati"
        dati.update(form.cleaned_data)

    # Quali di questi campi vanno nella persona?
    campi_persona = [str(x.name) for x in Persona._meta.get_fields() if not x.is_relation]
    dati_persona = {x: dati[x] for x in dati if x in campi_persona}

    # Crea la persona
    p = Persona(**dati_persona)
    p.email_contatto = dati['email']
    p.save()

    # Associa l'utenza
    u = Utenza(persona=p, email=dati['email'])
    u.set_password(dati['password'])
    u.save()

    # Effettua il login!
    u.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, u)

    # Da' il benvenuto all'utente
    p.invia_email_benvenuto_registrazione(tipo=tipo)

    redirect_url = "/utente/"

    if tipo == TIPO_ASPIRANTE:
        #  Genera semplicemente oggetto aspirante.
        p.ottieni_o_genera_aspirante()
        redirect_url = "/aspirante/"

    elif tipo == TIPO_VOLONTARIO:
        #  Richiede appartenenza come Volontario.
        a = Appartenenza(
            persona=p,
            inizio=dati['inizio'],
            sede=dati['sede'],
            membro=Appartenenza.VOLONTARIO,
        )
        a.save()
        a.richiedi()

    elif tipo == TIPO_DIPENDENTE:
        #  Richiede appartenenza come Dipendente.
        a = Appartenenza(
            persona=p,
            inizio=dati['inizio'],
            sede=dati['sede'],
            membro=Appartenenza.DIPENDENTE,
        )
        a.save()
        a.richiedi()

    else:
        raise ValueError("Non so come gestire questa iscrizione.")

    return redirect(redirect_url)


@pagina_privata
def utente(request, me):
    articoli = get_articoli(me)
    contesto = {
        "articoli": articoli[:5],
    }
    return 'anagrafica_utente_home.html', contesto


@pagina_privata
def utente_anagrafica(request, me):
    from .forms import ModuloProfiloModificaAnagraficaDomicilio

    context = {
        "delegati": me.deleghe_anagrafica(),
    }

    form_residenza = ModuloModificaAnagrafica(request.POST or None, instance=me)
    form_domicilio = ModuloProfiloModificaAnagraficaDomicilio(request.POST or None, instance=me)

    if request.POST:
        if form_residenza.is_valid() and form_domicilio.is_valid():
            cd_residenza = form_residenza.cleaned_data
            cd_domicilio = form_domicilio.cleaned_data

            if True == cd_domicilio['domicilio_uguale_a_residenza']:
                for f in ('indirizzo', 'comune', 'provincia', 'stato', 'cap'):
                    domicilio_key = 'domicilio_%s' % f
                    residenza_value = cd_residenza['%s_residenza' % f]
                    setattr(form_domicilio.instance, domicilio_key, residenza_value)

            form_residenza.save()
            form_domicilio.save()

            messages.success(request, "I tuoi dati anagrafici sono stati salvati correttamente.")
            return redirect(reverse('utente:anagrafica'))
    else:
        form_residenza = ModuloModificaAnagrafica(instance=me)
        form_domicilio = ModuloProfiloModificaAnagraficaDomicilio(instance=me)

    context.update({
        "form_residenza": form_residenza,
        "form_domicilio": form_domicilio,
    })

    return 'anagrafica_utente_anagrafica.html', context


@pagina_privata
def utente_fotografia(request, me):
   return redirect(reverse('utente:avatar'))


@pagina_privata
def utente_fotografia_avatar(request, me):

    modulo_avatar = ModuloModificaAvatar(request.POST or None, request.FILES or None, instance=me)

    if request.POST:
        if modulo_avatar.is_valid():
            modulo_avatar.save()

    contesto = {
        "modulo_avatar": modulo_avatar
    }

    return 'anagrafica_utente_fotografia_avatar.html', contesto


@pagina_privata
def utente_fotografia_fototessera(request, me):
    if not me.volontario:
        return errore_no_volontario(request, me)

    modulo_fototessera = ModuloNuovaFototessera(request.POST or None, request.FILES or None)

    sede = me.comitato_riferimento()

    if not sede:
        return errore_nessuna_appartenenza(
            request, me, torna_url="/utente/fotografia/avatar/"
        )

    if request.POST:

        if modulo_fototessera.is_valid():

            # Ritira eventuali richieste in attesa
            if me.fototessere_pending().exists():
                for x in me.fototessere_pending():
                    x.autorizzazioni_ritira()

            # Crea la fototessera
            fototessera = modulo_fototessera.save(commit=False)
            fototessera.persona = me
            fototessera.save()

            # Richiede l'autorizzazione
            fototessera.autorizzazione_richiedi_sede_riferimento(
                me, INCARICO_GESTIONE_FOTOTESSERE,
                invia_notifica_ufficio_soci=True,
                invia_notifica_presidente=True
            )


    contesto = {
        "modulo_fototessera": modulo_fototessera
    }

    return 'anagrafica_utente_fotografia_fototessera.html', contesto


@pagina_privata
def utente_documenti(request, me):
    if me.volontario or me.dipendente or me.ha_aspirante:
        pass
    else:
        return errore_no_volontario(request, me)

    context = {
        'documenti': me.documenti.all()
    }

    if request.method == 'POST':
        doc = Documento(persona=me)
        form = ModuloCreazioneDocumento(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            return redirect(reverse('utente:documenti'))
    else:
        form = ModuloCreazioneDocumento()

    context.update({'modulo_aggiunta': form})
    return 'anagrafica_utente_documenti.html', context


@pagina_privata
def utente_documenti_cancella(request, me, pk):
    doc = get_object_or_404(Documento, pk=pk)

    if not doc.persona == me:
        return redirect('/errore/permessi/')

    if doc.can_be_deleted:
        doc.delete()
    else:
        messages.error(request, 'Questo documento non può essere cancellato')

    return redirect(reverse('utente:documenti'))


@pagina_privata
def utente_documenti_zip(request, me):

    if not me.documenti.exists():
        return redirect('/utente/documenti')

    z = Zip(oggetto=me)
    for d in me.documenti.all():
        z.aggiungi_file(d.file.path)
    z.comprimi_e_salva(nome='Documenti.zip')

    return redirect(z.download_url)


@pagina_privata
def utente_storico(request, me):

    contesto = {
        "appartenenze": me.appartenenze.all(),
        "deleghe": me.deleghe.all()
    }

    return 'anagrafica_utente_storico.html', contesto


@pagina_privata
def utente_privacy(request, me):

    modulo = ModuloModificaPrivacy(request.POST or None, instance=me)

    if modulo.is_valid():
        modulo.save()

    contesto = {
        "modulo": modulo
    }
    return 'anagrafica_utente_privacy.html', contesto


@pagina_privata
def utente_contatti(request, me):

    parametri_cambio_email = {
        'contatto': {
            'session_key': 'modifica_contatto_id',
            'session_code': 'modifica_contatto',
            'code_type': 'code_c',
            'precedente': me.email_contatto,
            'field': 'email_contatto',
            'oggetto': 'Modifica email di contatto',
            'template': 'email_conferma_contatto.html',
        },
        'accesso': {
            'session_key': 'modifica_mail_id',
            'session_code': 'modifica_mail',
            'code_type': 'code_m',
            'precedente': me.utenza.email,
            'field': 'email',
            'oggetto': 'Modifica email di accesso',
            'template': 'email_conferma_cambio_email.html',
        },
    }

    if parametri_cambio_email['accesso']['session_key'] not in request.session:
        request.session[parametri_cambio_email['accesso']['session_key']] = get_random_string(length=32)
    if parametri_cambio_email['contatto']['session_key'] not in request.session:
        request.session[parametri_cambio_email['contatto']['session_key']] = get_random_string(length=32)

    stato_conferma_accesso = None
    stato_conferma_contatto = None
    errore_conferma_accesso = None
    errore_conferma_contatto = None

    if request.method == 'POST':

        modulo_email_accesso = ModuloModificaEmailAccesso(request.POST, instance=me.utenza)
        modulo_email_contatto = ModuloModificaEmailContatto(request.POST, instance=me)
        modulo_numero_telefono = ModuloCreazioneTelefono(request.POST)

        if modulo_email_accesso.is_valid():
            _richiesta_conferma_email(request, me, parametri_cambio_email['accesso'], modulo_email_accesso)

        if modulo_email_contatto.is_valid():
            _richiesta_conferma_email(request, me, parametri_cambio_email['contatto'], modulo_email_contatto)

        if modulo_numero_telefono.is_valid():
            me.aggiungi_numero_telefono(
                modulo_numero_telefono.data['numero_di_telefono'],
                modulo_numero_telefono.data['tipologia'] == modulo_numero_telefono.SERVIZIO
            )

    else:

        stato_conferma_accesso, errore_conferma_accesso = _conferma_email(request, me, parametri_cambio_email['accesso'])
        stato_conferma_contatto, errore_conferma_contatto = _conferma_email(request, me, parametri_cambio_email['contatto'])

        modulo_email_accesso = ModuloModificaEmailAccesso(instance=me.utenza)
        modulo_email_contatto = ModuloModificaEmailContatto(instance=me)
        modulo_numero_telefono = ModuloCreazioneTelefono()

    numeri = me.numeri_telefono.all()
    contesto = {
        'modulo_email_accesso': modulo_email_accesso,
        'modulo_email_contatto': modulo_email_contatto,
        'modulo_numero_telefono': modulo_numero_telefono,
        'numeri': numeri,
        'attesa_conferma_accesso': request.session.get(parametri_cambio_email['accesso']['session_code'], False),
        'attesa_conferma_contatto': request.session.get(parametri_cambio_email['contatto']['session_code'], False),
        'stato_conferma_accesso': stato_conferma_accesso,
        'stato_conferma_contatto': stato_conferma_contatto,
        'errore_conferma_accesso': errore_conferma_accesso,
        'errore_conferma_contatto': errore_conferma_contatto,
    }

    return 'anagrafica_utente_contatti.html', contesto


@pagina_privata
def utente_rubrica_referenti(request, me):
    if not me.volontario:
        return errore_no_volontario(request, me)
    sedi_volontario = Sede.objects.filter(pk__in=me.sedi_attuali(membro__in=Appartenenza.MEMBRO_RUBRICA).values_list("id", flat=True))
    referenti = Persona.objects.filter(
        Delega.query_attuale(
            oggetto_tipo=ContentType.objects.get_for_model(Sede),
            oggetto_id__in=sedi_volontario,
            tipo__in=DELEGHE_RUBRICA,
        ).via("delega")
    ).order_by('nome', 'cognome', 'codice_fiscale')\
        .distinct('nome', 'cognome', 'codice_fiscale')

    contesto = {
        "referenti": referenti,
    }
    return 'anagrafica_utente_rubrica_referenti.html', contesto


@pagina_privata
def utente_rubrica_volontari(request, me):
    if not me.volontario:
        return errore_no_volontario(request, me)
    sedi_volontario = Sede.objects.filter(pk__in=me.sedi_attuali(membro__in=Appartenenza.MEMBRO_RUBRICA).values_list("id", flat=True))
    sedi_gestione = me.oggetti_permesso(ELENCHI_SOCI)
    volontari_volontario = Persona.objects.filter(
        Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_RUBRICA, sede__in=sedi_volontario).via("appartenenze"),
        privacy_contatti__gte=Persona.POLICY_SEDE,
    )
    #volontari_gestione = Persona.objects.filter(
    #    Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_RUBRICA, sede__in=sedi_gestione).via("appartenenze"),
    #    privacy_contatti__gte=Persona.POLICY_RISTRETTO,
    #)
    volontari = volontari_volontario #  | volontari_gestione
    volontari = volontari\
        .prefetch_related('appartenenze', 'fototessere')\
        .order_by('nome', 'cognome', 'codice_fiscale')\
        .distinct('nome', 'cognome', 'codice_fiscale')
    ci_sono = volontari_volontario.filter(pk=me.pk).exists()

    contesto = {
        "volontari": volontari,
        "ci_sono": ci_sono,
    }
    return 'anagrafica_utente_rubrica_volontari.html', contesto

@pagina_privata
def utente_rubrica_servizio_civile(request, me):
    sedi_servizio_civile = Sede.objects.filter(pk__in=me.sedi_attuali().values_list("id", flat=True))
    servizio_civile = Persona.objects.filter(
        Appartenenza.query_attuale(membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE, sede__in=sedi_servizio_civile).via("appartenenze")
    )

    servizio_civile = servizio_civile \
        .prefetch_related('appartenenze', 'fototessere') \
        .order_by('nome', 'cognome', 'codice_fiscale') \
        .distinct('nome', 'cognome', 'codice_fiscale')
    contesto = {
        "servizio_civile": servizio_civile,
    }
    return 'anagrafica_utente_rubrica_servizio_civile.html', contesto


def _rubrica_delegati(me, delega, sedi_delega):
    return ElencoDelegati(sedi_delega.values_list('pk', flat=True), deleghe=[delega], me_id=me.pk)


@pagina_privata
def rubrica_delegati(request, me, rubrica):
    if rubrica not in RUBRICHE_TITOLI:
        return redirect('/utente/')

    delega, titolo, espandi = RUBRICHE_TITOLI[rubrica]
    deleghe = me.deleghe_attuali().filter(
        tipo=delega,
        oggetto_tipo=ContentType.objects.get_for_model(Sede),
    )

    sedi_delega = me.sedi_deleghe_attuali(espandi=True, deleghe=deleghe).espandi(pubblici=espandi)

    if request.POST:  # Ho selezionato delle sedi. Elabora elenco.

        sedi_delega = sedi_delega.filter(pk__in=request.POST.getlist('sedi'))
        elenco = _rubrica_delegati(me, delega, sedi_delega)
        contesto = {
            "elenco": elenco,
            "delega": delega,
            "elenco_nome": "Rubrica {}".format(titolo),
            "sedi": sedi_delega,
        }
        return 'anagrafica_delegato_rubrica_delegati.html', contesto

    else:  # Devo selezionare delle Sedi.

        return 'anagrafica_elenco_sede.html', {
            "sedi": sedi_delega,
            "elenco_nome": titolo,
            "elenco_template": 'anagrafica_delegato_rubrica_delegati.html',
        }


@pagina_privata
def utente_contatti_cancella_numero(request, me, pk):

    tel = get_object_or_404(Telefono, pk=pk)

    if not tel.persona == me:
        return redirect('/errore/permessi/')

    tel.delete()
    return redirect('/utente/contatti/')


@pagina_privata
def utente_donazioni_profilo(request, me):

    modulo = ModuloDonatore(request.POST or None, instance=me.donatore if hasattr(me, 'donatore') else None)

    if modulo.is_valid():

        if hasattr(me, 'donatore'):
            modulo.save()

        else:
            donatore = modulo.save(commit=False)
            donatore.persona = me
            donatore.save()

    contesto = {
        "modulo": modulo
    }
    return 'anagrafica_utente_donazioni_profilo.html', contesto


@pagina_privata
def utente_donazioni_sangue(request, me):
    modulo = ModuloDonazione(request.POST or None)

    if modulo.is_valid():

        donazione = modulo.save(commit=False)
        donazione.persona = me
        donazione.save()
        donazione.richiedi()

    donazioni = me.donazioni_sangue.all()

    contesto = {
        "modulo": modulo,
        "donazioni": donazioni
    }
    return 'anagrafica_utente_donazioni_sangue.html', contesto


@pagina_privata
def utente_donazioni_sangue_cancella(request, me, pk):
    donazione = get_object_or_404(Donazione, pk=pk)
    if not donazione.persona == me:
        return redirect(ERRORE_PERMESSI)

    donazione.delete()
    return redirect("/utente/donazioni/sangue/")


def estensioni_pending(me):

    delegati = []
    persone = []
    for estensione in me.estensioni_in_attesa():
        for autorizzazione in estensione.autorizzazioni:
            for persona in autorizzazione.espandi_notifiche(me.sede_riferimento(), [], True, True):
                if persona not in persone:
                    delegati.extend(persona.deleghe_attuali(
                        oggetto_id=me.sede_riferimento().pk, oggetto_tipo=ContentType.objects.get_for_model(Sede))
                    )
                    persone.append(persona)
    return me.estensioni_in_attesa(), delegati


@pagina_privata
def utente_estensione(request, me):
    if not me.sede_riferimento():
        return errore_nessuna_appartenenza(request, me)
    if not me.volontario:
        return errore_no_volontario(request, me)
    storico = me.estensioni.all()
    form = ModuloCreazioneEstensione(request.POST or None)
    if form.is_valid():
        est = form.save(commit=False)
        if est.destinazione in me.sedi_attuali():
            form.add_error('destinazione', 'Sei già appartenente a questa sede.')
        elif est.destinazione in [x.destinazione for x in me.estensioni_attuali_e_in_attesa()]:
            form.add_error('destinazione', 'Estensione già richiesta a questa sede.')
        else:
            est.richiedente = me
            est.persona = me
            est.save()
            est.richiedi()

            # Messaggio.costruisci_e_invia(
            #     oggetto="Richiesta di estensione",
            #     modello="email_richiesta_estensione.html",
            #     corpo={
            #         "trasferimento": est,
            #     },
            #     mittente=None,
            #     destinatari=[
            #         est.persona,
            #     ]
            # )
            # Messaggio.costruisci_e_invia(
            #     oggetto="Richiesta di estensione",
            #     modello="email_richiesta_estensione_cc.html",
            #     corpo={
            #         "trasferimento": est,
            #     },
            #     mittente=None,
            #     destinatari=[
            #         ##presidente sede di estensione
            #     ]
            # )
            # Avviso al Presidente dove è Volontario
            # Messaggio.costruisci_e_accoda(
            #     oggetto="Richiesta di estensione di un membro diretto",
            #     modello="email_richiesta_estensione_presidente.html",
            #     corpo={
            #         "estensione": est,
            #     },
            #     mittente=None,
            #     destinatari=[
            #         est.persona.sede_riferimento(membro=[Appartenenza.VOLONTARIO]).presidente()
            #     ]
            # )

    in_attesa, delegati = estensioni_pending(me)

    contesto = {
        "modulo": form,
        "storico": storico,
        "attuali": me.estensioni_attuali(),
        "in_attesa": in_attesa,
        "delegati": delegati,
    }
    return "anagrafica_utente_estensione.html", contesto


@pagina_privata()
def utente_estensione_termina(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    estensione = get_object_or_404(Estensione, pk=pk)
    if not estensione.persona == me:
        return redirect(ERRORE_PERMESSI)
    else:
        estensione.termina()
        return redirect('/utente/')


def utente_trasferimento_termina(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    trasferimento = get_object_or_404(Trasferimento, pk=pk)
    if not trasferimento.persona == me:
        return redirect(ERRORE_PERMESSI)
    else:
        trasferimento.ritira()
        return redirect('/utente/trasferimento/')


def trasferimenti_pending(me):

    trasferimento = me.trasferimento
    trasferimenti_auto_pending = None
    trasferimenti_manuali_pending = None
    persone = OrderedDict()
    persone[PERMESSI_NOMI_DICT[PRESIDENTE]] = set()
    persone[PERMESSI_NOMI_DICT[UFFICIO_SOCI]] = set()
    if trasferimento:
        sedi = (me.sede_riferimento().pk, me.comitato_riferimento().pk)
        if me.sede_riferimento().estensione == TERRITORIALE:
            persone[PERMESSI_NOMI_DICT[UFFICIO_SOCI_UNITA]] = set()
        for autorizzazione in trasferimento.autorizzazioni:
            delegati = autorizzazione.espandi_notifiche(me.sede_riferimento(), [], True, True)
            if me.sede_riferimento().estensione == TERRITORIALE:
                delegati.extend(autorizzazione.espandi_notifiche(me.comitato_riferimento(), [], True, True))
            for persona in delegati:
                deleghe = persona.deleghe_attuali(
                    oggetto_id__in=sedi, oggetto_tipo=ContentType.objects.get_for_model(Sede)
                ).values_list('tipo', flat=True)
                if PRESIDENTE in deleghe:
                    persone[PERMESSI_NOMI_DICT[PRESIDENTE]].add(persona)
                elif UFFICIO_SOCI in deleghe and PERMESSI_NOMI_DICT[UFFICIO_SOCI] in persone:
                    persone[PERMESSI_NOMI_DICT[UFFICIO_SOCI]].add(persona)
                elif UFFICIO_SOCI_UNITA in deleghe and PERMESSI_NOMI_DICT[UFFICIO_SOCI_UNITA] in persone:
                    persone[PERMESSI_NOMI_DICT[UFFICIO_SOCI_UNITA]].add(persona)
        if trasferimento.con_scadenza:
            trasferimenti_auto_pending = trasferimento
        else:
            trasferimenti_manuali_pending = trasferimento
    return trasferimenti_auto_pending, trasferimenti_manuali_pending, persone


@pagina_privata
def utente_trasferimento(request, me):
    if not me.sede_riferimento():
        return errore_nessuna_appartenenza(request, me)

    if not me.volontario:
        return errore_no_volontario(request, me)
    storico = me.trasferimenti.all()

    form = ModuloCreazioneTrasferimento(request.POST or None)
    if form.is_valid():
        trasf = form.save(commit=False)
        if trasf.destinazione in me.sedi_attuali(membro=Appartenenza.VOLONTARIO):
            form.add_error('destinazione', 'Sei già appartenente a questa sede.')
        #elif trasf.destinazione.comitato != me.sede_riferimento().comitato and True:##che in realta' e' il discriminatore delle elezioni
        #    return errore_generico(request, me, messaggio="Non puoi richiedere un trasferimento tra comitati durante il periodo elettorale")
        elif me.trasferimento:
            return errore_generico(request, me, messaggio="Non puoi richiedere piú di un trasferimento alla volta")
        else:
            trasf.persona = me
            trasf.richiedente = me
            trasf.save()
            trasf.richiedi()

            # Avviso a se stesso
            Messaggio.costruisci_e_accoda(
                oggetto="Richiesta di trasferimento",
                modello="email_richiesta_trasferimento.html",
                corpo={
                    "trasferimento": trasf,
                },
                mittente=None,
                destinatari=[
                    trasf.persona,
                ]
            )

            # Avviso al Presidente di Sede Destinazione
            Messaggio.costruisci_e_accoda(
                oggetto="Richiesta di trasferimento in entrata",
                modello="email_richiesta_trasferimento_cc.html",
                corpo={
                    "trasferimento": trasf,
                },
                mittente=None,
                destinatari=[
                    trasf.destinazione.presidente()
                ]
            )

            # Avviso al Presidente dove è Dipendente (o MEMBRO_DIRETTO)
            # Messaggio.costruisci_e_accoda(
            #     oggetto="Richiesta di trasferimento",
            #     modello="email_richiesta_trasferimento_presidente.html",
            #     corpo={
            #         "trasferimento": trasf,
            #     },
            #     mittente=None,
            #     destinatari=[
            #         trasf.persona.sede_riferimento().presidente()
            #     ]
            # )

    trasferimenti_auto_pending, trasferimenti_manuali_pending, delegati = trasferimenti_pending(me)

    contesto = {
        "modulo": form,
        "storico": storico,
        "trasferimenti_auto_pending": trasferimenti_auto_pending,
        "trasferimenti_manuali_pending": trasferimenti_manuali_pending,
        "delegati": delegati,
    }
    return "anagrafica_utente_trasferimento.html", contesto


@pagina_privata
def utente_riserva(request, me):
    if not me.volontario:
        return errore_no_volontario(request, me)
    if not me.appartenenze_attuali() or not me.sede_riferimento():
        return errore_generico(titolo="Errore", messaggio="Si è verificato un errore generico.", request=request)
    storico = me.riserve.all()
    form = ModuloCreazioneRiserva(request.POST or None)
    if form.is_valid():
        r = form.save(commit=False)

        r.persona = me
        r.appartenenza = me.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        r.save()
        r.richiedi()

        # Messaggio.costruisci_e_accoda(
        #     oggetto="Richiesta di riserva di un membro diretto",
        #     modello="email_richiesta_riserva_presidente.html",
        #     corpo={
        #         "riserva": r,
        #     },
        #     mittente=None,
        #     destinatari=[
        #         r.persona.sede_riferimento().presidente()
        #     ]
        # )

        return messaggio_generico(request, me, titolo="Riserva registrata",
                                      messaggio="La riserva è stato registrata con successo",
                                      torna_titolo="Torna alla dash",
                                      torna_url="/utente/")
    contesto = {
        "modulo": form,
        "storico": storico,
    }
    return "anagrafica_utente_riserva.html", contesto


@pagina_privata
def utente_riserva_ritira(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    riserva = get_object_or_404(Riserva, pk=pk)
    if not riserva.persona == me:
        return redirect(ERRORE_PERMESSI)
    riserva.autorizzazioni_ritira()
    Messaggio.costruisci_e_invia(
           oggetto="Riserva terminata",
           modello="email_richiesta_riserva_terminata.html",
           corpo={
               "riserva": riserva,
           },
           mittente=riserva.persona,
           destinatari=[
                riserva.persona.sede_riferimento().presidente()
           ]
        )
    return redirect("/utente/")


@pagina_privata
def utente_riserva_termina(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    riserva = get_object_or_404(Riserva, pk=pk)
    if not riserva.persona == me:
        return redirect(ERRORE_PERMESSI)
    riserva.termina()
    return redirect("/utente/")


@pagina_privata
def utente_estensione_estendi(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    estensione = get_object_or_404(Estensione, pk=pk)
    if not estensione.persona == me:
        return redirect(ERRORE_PERMESSI)
    estensione.appartenenza.fine = datetime.date.today()+datetime.timedelta(days=365)
    estensione.appartenenza.save()
    return redirect("/utente/estensione")


@pagina_privata
def utente_trasferimento_ritira(request, me, pk):
    if not me.volontario:
        return errore_no_volontario(request, me)
    trasf = get_object_or_404(Trasferimento, pk=pk)
    if not trasf.persona == me:
        return redirect(ERRORE_PERMESSI)
    trasf.autorizzazioni_ritira()
    return redirect("/utente/trasferimento/")


@pagina_privata
def profilo_messaggio(request, me, pk=None):
    persona = get_object_or_404(Persona, pk=pk)
    qs = Persona.objects.filter(pk=persona.pk)
    return imposta_destinatari_e_scrivi_messaggio(request, qs)


@pagina_privata
def profilo_turni_foglio(request, me, pk=None):
    persona = get_object_or_404(Persona, pk=pk)
    if not me.permessi_almeno(persona, LETTURA):
        return redirect(ERRORE_PERMESSI)
    excel = persona.genera_foglio_di_servizio()
    return redirect(excel.download_url)


@pagina_privata
def strumenti_delegati(request, me):
    from formazione.forms import FormCreateDirettoreDelega

    # Get values stored in the session
    session = request.session
    app_label = session['app_label']
    model = session['model']
    pk = int(session['pk'])
    continua_url = session['continua_url']
    almeno = session['almeno']
    delega = session['delega']

    # Get object
    oggetto = apps.get_model(app_label, model).objects.get(pk=pk)

    # Instantiate a new form
    form_data = {
        'oggetto': oggetto,
        'me': me,
        'initial': {'inizio': datetime.date.today()},
    }
    form = ModuloCreazioneDelega(request.POST or None, **form_data)
    if model == 'corsobase':
        form = FormCreateDirettoreDelega(request.POST or None, **form_data)

    # Check form is valid
    if form.is_valid():
        d = form.save(commit=False)

        if oggetto.deleghe.all().filter(Delega.query_attuale().q, tipo=delega, persona=d.persona).exists():
            return errore_generico(
                request, me,
                titolo="%s è già delegato" % (d.persona.nome_completo,),
                messaggio="%s ha già una delega attuale come %s per %s" % (d.persona.nome_completo, PERMESSI_NOMI_DICT[delega], oggetto),
                torna_titolo="Torna indietro",
                torna_url=reverse('strumenti_delegati'),
            )

        if model == 'corsobase':
            from formazione.training_api import TrainingApi
            api = TrainingApi()
            api.aggiugi_ruolo(persona=d.persona, corso=oggetto, ruolo=TrainingApi.DIRETTORE)

        d.inizio = poco_fa()
        d.firmatario = me
        d.tipo = delega
        d.oggetto = oggetto
        d.save()
        d.invia_notifica_creazione()

    deleghe = oggetto.deleghe.filter(tipo=delega)
    deleghe_attuali = oggetto.deleghe_attuali(tipo=delega)

    context = {
        "continua_url": continua_url,
        "almeno": almeno,
        "delega": PERMESSI_NOMI_DICT[delega],
        "modulo": form,
        "oggetto": oggetto,
        "deleghe": deleghe,
        "deleghe_attuali": deleghe_attuali,
    }

    return 'anagrafica_strumenti_delegati.html', context


@pagina_privata
def strumenti_delegati_termina(request, me, delega_pk=None):
    app_label = request.session['app_label']
    model = request.session['model']
    pk = int(request.session['pk'])
    continua_url = request.session['continua_url']
    almeno = request.session['almeno']
    delega = request.session['delega']
    oggetto = apps.get_model(app_label, model)
    oggetto = oggetto.objects.get(pk=pk)

    delega = get_object_or_404(Delega, pk=delega_pk)
    if not me.permessi_almeno(delega.oggetto, GESTIONE):
        return redirect(ERRORE_PERMESSI)

    delega.termina(mittente=me, termina_at=poco_fa())
    return redirect(reverse('strumenti_delegati'))


@pagina_privata
def utente_curriculum(request, me, tipo=None):

    if not tipo:
        return redirect("/utente/curriculum/CP/")

    if tipo not in dict(Titolo.TIPO):  # Tipo permesso?
        redirect(ERRORE_PERMESSI)

    if tipo in (Titolo.PATENTE_CRI, Titolo.TITOLO_CRI) and not (me.volontario or me.dipendente):
        return errore_no_volontario(request, me)

    passo = 1
    tipo_display = dict(Titolo.TIPO)[tipo]
    request.session['titoli_tipo'] = tipo

    valida_secondo_form = True
    titolo_selezionato = None
    modulo = ModuloNuovoTitoloPersonale(tipo,
                                        tipo_display,
                                        request.POST or None,
                                        me=me)
    if modulo.is_valid():
        titolo_selezionato = modulo.cleaned_data['titolo']
        passo = 2
        valida_secondo_form = False

    if 'titolo_selezionato_id' in request.POST:
        titolo_selezionato = Titolo.objects.get(pk=request.POST['titolo_selezionato_id'])
        passo = 2

    if passo == 2:
        modulo = ModuloDettagliTitoloPersonale(request.POST if request.POST and valida_secondo_form else None)

        if not titolo_selezionato.richiede_data_ottenimento:
            del modulo.fields['data_ottenimento']

        if not titolo_selezionato.richiede_data_scadenza:
            del modulo.fields['data_scadenza']

        if not titolo_selezionato.richiede_luogo_ottenimento:
            del modulo.fields['luogo_ottenimento']

        if not titolo_selezionato.richiede_codice:
            del modulo.fields['codice']

        if modulo.is_valid():

            tp = modulo.save(commit=False)
            tp.persona = me
            tp.titolo = titolo_selezionato
            tp.save()

            if titolo_selezionato.richiede_conferma:
                sede_attuale = me.sede_riferimento()
                if not sede_attuale:
                    tp.delete()
                    return errore_nessuna_appartenenza(
                        request, me,
                        torna_url="/utente/curriculum/%s/" % (tipo,),
                    )

                tp.autorizzazione_richiedi_sede_riferimento(
                    me, INCARICO_GESTIONE_TITOLI
                )
            return redirect("/utente/curriculum/%s/?inserimento=ok" % (tipo,))

    titoli = me.titoli_personali.all().filter(titolo__tipo=tipo).order_by('data_scadenza')

    contesto = {
        "tipo": tipo,
        "tipo_display": tipo_display,
        "passo": passo,
        "modulo": modulo,
        "titoli": titoli,
        "titolo": titolo_selezionato
    }
    return 'anagrafica_utente_curriculum.html', contesto


@pagina_privata
def utente_curriculum_cancella(request, me, pk=None):

    titolo_personale = get_object_or_404(TitoloPersonale, pk=pk)
    if not titolo_personale.persona == me:
        return redirect(ERRORE_PERMESSI)

    tipo = titolo_personale.titolo.tipo
    titolo_personale.delete()

    return redirect("/utente/curriculum/%s/" % (tipo,))


@pagina_privata
def profilo_documenti_cancella(request, me, pk, documento_pk):
    persona = get_object_or_404(Persona, pk=pk)
    documento = get_object_or_404(Documento, pk=documento_pk)
    if (not me.permessi_almeno(persona, MODIFICA)) or not (documento.persona == persona):
        return redirect(ERRORE_PERMESSI)
    documento.delete()
    return redirect("/profilo/%d/documenti/" % (persona.pk,))


@pagina_privata
def profilo_curriculum_cancella(request, me, pk, tp_pk):
    persona = get_object_or_404(Persona, pk=pk)
    titolo_personale = get_object_or_404(TitoloPersonale, pk=tp_pk)
    if (not me.permessi_almeno(persona, MODIFICA)) or not (titolo_personale.persona == persona):
        return redirect(ERRORE_PERMESSI)
    titolo_personale.delete()
    return redirect("/profilo/%d/curriculum/" % (persona.pk,))


@pagina_privata
def profilo_sangue_cancella(request, me, pk, donazione_pk):
    persona = get_object_or_404(Persona, pk=pk)
    donazione = get_object_or_404(Donazione, pk=donazione_pk)
    if (not me.permessi_almeno(persona, MODIFICA)) or not (donazione.persona == persona):
        return redirect(ERRORE_PERMESSI)
    donazione.delete()
    return redirect("/profilo/%d/sangue/" % (persona.pk,))


@pagina_privata
def profilo_telefono_cancella(request, me, pk, tel_pk):
    persona = get_object_or_404(Persona, pk=pk)
    telefono = get_object_or_404(Telefono, pk=tel_pk)
    if (not me.permessi_almeno(persona, MODIFICA)) or not (telefono.persona == persona):
        return redirect(ERRORE_PERMESSI)
    telefono.delete()
    return redirect("/profilo/%d/anagrafica/" % (persona.pk,))


@pagina_privata
def presidente(request, me):
    sedi = me.oggetti_permesso(GESTIONE_SEDE)
    sede_presidente = sedi.order_by('level').first()
    contesto = {}
    if sede_presidente:
        contesto.update({
            "sedi": sedi,
            "sede_presidente": sede_presidente
        })
    return 'anagrafica_presidente.html', contesto


def _presidente_sede_ruoli(sede):

    sezioni = OrderedDict()

    sezioni.update({
        "Obiettivi Strategici": [
            (DELEGATO_OBIETTIVO_1, "Obiettivo Strategico I", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_1).count(), []),
            (DELEGATO_OBIETTIVO_2, "Obiettivo Strategico II", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_2).count(),[]),
            (DELEGATO_OBIETTIVO_3, "Obiettivo Strategico III", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_3).count(), []),
            (DELEGATO_OBIETTIVO_4, "Obiettivo Strategico IV", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_4).count(), []),
            (DELEGATO_OBIETTIVO_5, "Obiettivo Strategico V", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_5).count(), []),
            (DELEGATO_OBIETTIVO_6, "Obiettivo Strategico VI", sede.delegati_attuali(tipo=DELEGATO_OBIETTIVO_6).count(), []),
        ]

    })

    sezioni.update({
        "Responsabili": [
            (UFFICIO_SOCI, "Ufficio Soci", sede.delegati_attuali(tipo=UFFICIO_SOCI).count(), []),
            (UFFICIO_SOCI_UNITA, "Ufficio Soci per Unità territoriale", sede.delegati_attuali(tipo=UFFICIO_SOCI_UNITA).count(), []),
            (UFFICIO_SOCI_CM, "Ufficio Soci Corpo militare", sede.delegati_attuali(tipo=UFFICIO_SOCI_CM).count(), []),
            (UFFICIO_SOCI_IIVV, "Ufficio Soci Infermiere volontarie", sede.delegati_attuali(tipo=UFFICIO_SOCI_IIVV).count(), []),
            (RESPONSABILE_FORMAZIONE, "Formazione", sede.delegati_attuali(tipo=RESPONSABILE_FORMAZIONE).count(), []),
            (RESPONSABILE_AUTOPARCO, "Autoparco", sede.delegati_attuali(tipo=RESPONSABILE_AUTOPARCO).count(), []),
            (DELEGATO_CO, "Centrale Operativa", sede.delegati_attuali(tipo=DELEGATO_CO).count(), []),
        ]
    })

    sezioni.update({
        "Cariche elettive": [
            (VICE_PRESIDENTE, "Vice Presidente", sede.delegati_attuali(tipo=VICE_PRESIDENTE).count(), [sede.vice_presidente()] if sede.vice_presidente() else []),
            (CONSIGLIERE, "Consigliere", sede.delegati_attuali(tipo=CONSIGLIERE).count(), sede.consiglieri()),
            (CONSIGLIERE_GIOVANE, "Consigliere giovane", sede.delegati_attuali(tipo=CONSIGLIERE_GIOVANE).count(), [sede.consigliere_giovane()] if sede.consigliere_giovane() else []),
        ]
    })

    return sezioni


@pagina_privata
def presidente_sede(request, me, sede_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    form = ModuloPresidenteSede(request.POST or None, instance=sede)
    if form.is_valid():
        form.save()

    context = {
        "sede": sede,
        "modulo": form,
        "sezioni": _presidente_sede_ruoli(sede),
    }
    return 'anagrafica_presidente_sede.html', context


@pagina_privata
def presidente_sede_indirizzi(request, me, sede_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    form = ModuloPresidenteSede(request.POST or None, instance=sede)
    if form.is_valid():
        form.save()

    pdr_form = ModuloPresidenteSedePersonaDiRiferimento(request.POST or None,
                                                        instance=sede)
    if pdr_form.is_valid():
        pdr_form.save()

    context = {
        "sede": sede,
        "modulo": form,
    }

    # GAIA-280. Inizio della logica. La vista riceve un parametro GET.
    # Tutto il resto procede attraverso lo scambio di dati fra: templatetags, session
    # (commit 74347d34fe)
    modifica_indirizzo_sede = request.GET.get('f')
    if modifica_indirizzo_sede and modifica_indirizzo_sede in ['sede_operativa',
                                                               'indirizzo_per_spedizioni']:
        context['modifica_indirizzo_sede'] = modifica_indirizzo_sede

        if modifica_indirizzo_sede == "indirizzo_per_spedizioni":
            context['persona_di_riferimento_form'] = pdr_form

    else:
        return redirect(reverse('presidente:sedi_panoramico', args=[sede.pk,]))

    return 'anagrafica_presidente_sede_indirizzi.html', context


@pagina_privata
def presidente_sede_operativa_indirizzo(request, me, sede_pk, sede_operativa_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    action = request.GET.get('a')
    if action and action == 'cancella':
        sedi_operative = sede.sede_operativa
        sede_operativa = sedi_operative.get(pk=sede_operativa_pk)
        sedi_operative.remove(sede_operativa)
        sede.save()

        messages.success(request, "La sede operativa è stata cancellata.")
        return redirect(sede.presidente_url)

    return 'anagrafica_presidente_sede_operativa_indirizzo.html', {}


@pagina_privata
def presidente_sede_nominativi(request, me, sede_pk):
    redirect_to_sede = redirect(reverse('presidente:sedi_panoramico', args=[sede_pk,]))
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    tipo = None
    add_tipo = request.GET.get('add') or request.POST['tipo']
    if add_tipo in [Nominativo.REVISORE_DEI_CONTI,
                    Nominativo.ORGANO_DI_CONTROLLO]:
        tipo = add_tipo

    if not tipo:
        return redirect_to_sede

    form = ModuloPresidenteSedeNominativo(request.POST or None, tipo=tipo)
    if form.is_valid():
        cd = form.cleaned_data
        nominativo = form.save(commit=False)
        nominativo.tipo = cd['tipo']
        nominativo.sede = sede
        nominativo.inizio = timezone.now()
        nominativo.save()

        return redirect_to_sede

    context = {
        'form': form,
    }

    return 'anagrafica_presidente_sede_nominativi.html', context


@pagina_privata
def sede_nominativo_modifica(request, me, sede_pk, nominativo_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    nominativo = Nominativo.objects.get(pk=nominativo_pk)

    form = ModuloPresidenteSedeNominativo(request.POST or None, instance=nominativo)
    if form.is_valid():
        form.save()
        return redirect(nominativo.url())

    context = {
        'form': form,
        'nominativo': nominativo,
    }
    return 'anagrafica_sede_nominativo_modifica.html', context


@pagina_privata
def sede_nominativo_termina(request, me, sede_pk, nominativo_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    nominativo = Nominativo.objects.get(pk=nominativo_pk)

    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    # if nominativo.tipo == Nominativo.REVISORE_DEI_CONTI:
    #     tutti_nominativi_per_sede = Nominativo.objects.filter(sede=sede)
    #     if tutti_nominativi_per_sede.count() == 1:
    #         messages.error("")
    #         return sede.presidente_url

    nominativo.termina()

    return redirect(sede.presidente_url)


@pagina_privata
def presidente_checklist(request, me, sede_pk):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    from formazione.models import CorsoBase
    from attivita.models import Attivita

    deleghe_da_processare = [
        (UFFICIO_SOCI, sede),
        (UFFICIO_SOCI_CM, sede),
        (UFFICIO_SOCI_IIVV, sede),
        # (CONSIGLIERE, sede),
        (DELEGATO_OBIETTIVO_1, sede),
        (DELEGATO_OBIETTIVO_2, sede),
        (DELEGATO_OBIETTIVO_3, sede),
        (DELEGATO_OBIETTIVO_4, sede),
        (DELEGATO_OBIETTIVO_5, sede),
        (DELEGATO_OBIETTIVO_6, sede),
        (RESPONSABILE_FORMAZIONE, sede),
        (RESPONSABILE_AUTOPARCO, sede),
        (DELEGATO_CO, sede),
    ]

    for unita in sede.espandi():
        deleghe_da_processare += [
            (UFFICIO_SOCI_UNITA, unita)
        ]

    for corso in me.oggetti_permesso(GESTIONE_CORSO).filter(stato__in=[CorsoBase.PREPARAZIONE, CorsoBase.ATTIVO]):
        deleghe_da_processare += [
            (DIRETTORE_CORSO, corso)
        ]

    for area in me.oggetti_permesso(GESTIONE_ATTIVITA_AREA):
        deleghe_da_processare += [
            (RESPONSABILE_AREA, area),
        ]

    for attivita in me.oggetti_permesso(GESTIONE_ATTIVITA).filter(apertura=Attivita.APERTA):
        deleghe_da_processare += [
            (REFERENTE, attivita),
        ]

    deleghe = []
    progresso_si = 0
    for tipo, oggetto in deleghe_da_processare:
        delegati_attuali = oggetto.delegati_attuali(tipo=tipo)
        if delegati_attuali:
            progresso_si += 1
        ct = ContentType.objects.get_for_model(oggetto)
        deleghe += [
            (PERMESSI_NOMI_DICT[tipo], oggetto, delegati_attuali,
             "/presidente/checklist/%d/%s/%d/%d/" % (
                 sede.pk, tipo, ct.pk, oggetto.pk,
             )),
        ]

    progresso = int(progresso_si / len(deleghe) * 100)

    contesto = {
        "deleghe": deleghe,
        "sede": sede,
        "progresso": progresso,
        "progresso_si": progresso_si,
    }
    return "anagrafica_presidente_checklist.html", contesto


@pagina_privata
def presidente_checklist_delegati(request, me, sede_pk, tipo, oggetto_tipo, oggetto_id):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    oggetto = ContentType.objects.get(pk=oggetto_tipo).get_object_for_this_type(pk=oggetto_id)
    tipo_nome = PERMESSI_NOMI_DICT[tipo]

    continua_url = "/presidente/checklist/%d/" % sede.pk

    contesto = {
        "delega_oggetto": oggetto,
        "delega_tipo": tipo,
        "delega_tipo_nome": tipo_nome,
        "continua_url": continua_url,
    }
    return "anagrafica_presidente_checklist_delegati.html", contesto


@pagina_privata
def presidente_sede_delegati(request, me, sede_pk, delega):
    sede = get_object_or_404(Sede, pk=sede_pk)
    if not me.permessi_almeno(sede, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    contesto = {
        "sede": sede,
        "delega": delega,
        "continua_url": "/presidente/sedi/%d/" % (sede.pk,),
    }
    return 'anagrafica_presidente_sede_delegati.html', contesto


def handle_uploaded_file(f):
    nome = '/tmp/csv-%s.txt' % (genera_uuid_casuale(),)
    with open(nome, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return nome


@pagina_privata
def admin_import_volontari(request, me):
    from anagrafica.importa import import_valida_volontari

    if not me.utenza.is_superuser:
        return redirect(ERRORE_PERMESSI)

    risultati = []
    modulo = ModuloImportVolontari(request.POST or None, request.FILES or None)
    righe = []

    importati = 0

    def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
        csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
        for row in csv_reader:
            yield [cell.decode('UTF-8') if hasattr(cell, 'decode') else cell for cell in row]

    if modulo.is_valid():


        nome_file = handle_uploaded_file(request.FILES['file_csv'])
        with codecs.open(nome_file, encoding="utf-8") as csvfile:
            riga = unicode_csv_reader(csvfile, delimiter=modulo.cleaned_data['delimitatore'])
            intestazione = True
            for r in riga:
                if intestazione:
                    intestazione = False
                    continue
                righe += [r]

        try:
            risultati = import_valida_volontari(righe)
            if modulo.cleaned_data['azione'] == modulo.IMPORTA:
                importati = import_import_volontari(risultati)

        except IndexError:
            return errore_generico(request, me, titolo="Delimitatore errato",
                                   messaggio="File non valido o delimitatore errato")

        risultati = zip(righe, risultati)
    contesto = {
        "modulo": modulo,
        "risultati": risultati,
        "ERRORE": VALIDAZIONE_ERRORE,
        "AVVISO": VALIDAZIONE_AVVISO,
        "OK": VALIDAZIONE_OK,
        "importati": importati,
    }
    return 'admin_import_volontari.html', contesto


@pagina_privata
def admin_statistiche(request, me):
    if not me.utenza.is_staff:
        return redirect(ERRORE_PERMESSI)

    oggi = datetime.date.today()
    nascita_minima_35 = datetime.date(oggi.year - 36, oggi.month, oggi.day)
    persone = Persona.objects.all()
    soci = Persona.objects.filter(
        Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_SOCIO).via("appartenenze")
    ).distinct('nome', 'cognome', 'codice_fiscale')
    soci_giovani_35 = soci.filter(
        data_nascita__gt=nascita_minima_35,
    )
    sedi = Sede.objects.filter(attiva=True)
    comitati = sedi.comitati()
    regionali = Sede.objects.filter(estensione=REGIONALE).exclude(nome__contains='Provinciale Di Roma')

    totale_regione_soci = 0
    totale_regione_volontari = 0

    regione_soci_volontari = []
    for regione in regionali:
        regione_soci = int(regione.membri_attuali(figli=True, membro__in=Appartenenza.MEMBRO_SOCIO).count())
        regione_volontari = int(regione.membri_attuali(figli=True, membro=Appartenenza.VOLONTARIO).count())
        regione_soci_volontari += [
            (
                regione,
                regione_soci,
                regione_volontari,
            ),
        ]
        totale_regione_soci += regione_soci
        totale_regione_volontari += regione_volontari

    contesto = {
        "persone_numero": persone.count(),
        "soci_numero": soci.count(),
        "soci_percentuale": soci.count() / persone.count() * 100,
        "soci_giovani_35_numero": soci_giovani_35.count(),
        "soci_giovani_35_percentuale": soci_giovani_35.count() / soci.count() * 100,
        "sedi_numero": sedi.count(),
        "comitati_numero": comitati.count(),
        "ora": timezone.now(),
        "regione_soci_volontari": regione_soci_volontari,
        "totale_regione_soci": totale_regione_soci,
        "totale_regione_volontari": totale_regione_volontari,
    }
    return 'admin_statistiche.html', contesto


@pagina_privata
def admin_report_federazione(request, me):

    if not me.utenza.is_superuser:
        return redirect(ERRORE_PERMESSI)

    modulo = ModuloReportFederazione(request.POST or None,
                                     initial={"data": oggi()})
    contesto = {"modulo": modulo,}

    fasce_di_eta = [(0, 30), (30, 41), (41, 51), (51, 66), (66, 999)]
    # fasce_di_anzianita = [(0, 1), (1, 5), (5, 10), (10, 21), (21, 30), (30, 999)]

    if modulo.is_valid():

        volontari_per_fasce_di_eta = []
        tutti_volontari = Persona.objects.filter(Appartenenza
                                                 .query_attuale(al_giorno=modulo.cleaned_data['data'],
                                                                membro__in=Appartenenza.MEMBRO_SOCIO)
                                                 .via("appartenenze")) \
                                         .distinct('nome', 'cognome', 'codice_fiscale')

        for fascia_di_eta in fasce_di_eta:
            eta_minima, eta_massima = fascia_di_eta
            r = tutti_volontari.filter(Persona.query_eta_minima(eta_minima).q,
                                       Persona.query_eta_massima(eta_massima - 1).q) \
                               .count()
            volontari_per_fasce_di_eta.append((fascia_di_eta, r))

        decessi = Dimissione.objects.filter(motivo=Dimissione.DECEDUTO,
                                            creazione__gt=modulo.cleaned_data['data'] - datetime.timedelta(days=365),
                                            creazione__lte=modulo.cleaned_data['data']) \
                                    .count()

        contesto.update({"volontari_per_fasce_di_eta": volontari_per_fasce_di_eta,
                         "volontari": tutti_volontari.count(),
                         "decessi": decessi,})

    return 'admin_report_federazione.html', contesto


@pagina_privata
def admin_import_presidenti(request, me):

    def __get_presidiata(sede):
        """
            Ritorna delega del presidente o commissario se la sede è presidiata.
        """
        delega_presidente = sede.deleghe_attuali(
            al_giorno=datetime.datetime.now(), tipo=PRESIDENTE, fine=None
        ).first()
        delega_commissario = sede.deleghe_attuali(
            al_giorno=datetime.datetime.now(), tipo=COMMISSARIO, fine=None
        ).first()

        if delega_presidente and delega_commissario:
            # Ritorna l'ultimo in carica
            if int(delega_presidente.inizio.strftime('%s')) > int(delega_commissario.inizio.strftime('%s')):
                return delega_presidente, True
            else:
                return delega_commissario, False
        elif delega_presidente:
            # Ritorna Presidente
            return delega_presidente, True
        elif delega_commissario:
            # Ritorna Commissario
            return delega_commissario, False
        else:
            # Non è presidiata da nessuno
            return None, False

    if not me.utenza.is_superuser:
        return redirect(ERRORE_PERMESSI)

    # Numero di presidenti per pagina
    numero_presidenti_per_pagina = 15

    moduli = []
    esiti = []
    for i in range(0, numero_presidenti_per_pagina):
        modulo = ModuloImportPresidenti(request.POST or None, prefix="presidenti_%d" % i)

        msg = ""

        if modulo.is_valid():

            # Ottieni i dati
            nomina = modulo.cleaned_data['nomina']
            persona = modulo.cleaned_data['persona']
            sede = modulo.cleaned_data['sede']

            if nomina == PRESIDENTE or nomina == COMMISSARIO:
                # Prendo l'ultima delega da commissario/presidente per la sede
                delega_persona_precedente, isPresidente = __get_presidiata(sede)

                # Se una delle due figure esiste (Presidente/Commissario)
                if delega_persona_precedente:

                    # Se è già stato nominato in questa sede.
                    if delega_persona_precedente.persona == persona and isPresidente:
                        esiti += [
                            (
                                persona,
                                sede,
                                "Saltato. E' già {} di questa Sede.".format(
                                    'Presidente' if isPresidente else 'Commissario'
                                )
                            )
                        ]
                        continue

                    # Termina la Presidenza/Commissariato.
                    delega_persona_precedente.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())

                    # Termina tutte le Deleghe correlate.
                    delega_persona_precedente.presidenziali_termina_deleghe_dipendenti()

                # Controllo se è gia commissario di un altra sede
                gia_presidente = persona.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=PRESIDENTE, fine=None
                ).first()
                if gia_presidente:
                    gia_presidente.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())
                else:
                    gia_commissario = persona.deleghe_attuali(
                        al_giorno=datetime.datetime.now(), tipo=COMMISSARIO, fine=None
                    ).first()
                    if gia_commissario:
                        gia_commissario.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())

                    msg = "OK, Nomina effettuata."
                    if delega_persona_precedente:
                        msg += "Vecchio {} dimesso {}".format(
                            'Presidente' if isPresidente else 'Commissario',
                            delega_persona_precedente.persona.codice_fiscale
                        )
                    else:
                        msg += "Non vi era alcuna nomina."

            elif nomina == CONSIGLIERE:
                deleghe_consigliere = sede.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=CONSIGLIERE, fine=None
                )

                for delega in deleghe_consigliere:
                    # Se è già stato nominato in questa sede.
                    if delega.persona == persona:
                        esiti += [
                            (
                                persona,
                                sede,
                                "Saltato. E' già Consigliere di questa Sede."
                            )
                        ]
                        continue

                gia_consigliere = persona.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=CONSIGLIERE, fine=None
                ).first()

                if gia_consigliere:
                    gia_consigliere.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())

                msg = "OK, Nomina effettuata."
            elif nomina == CONSIGLIERE_GIOVANE:
                delega_consigliere_giovane = sede.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=CONSIGLIERE_GIOVANE, fine=None
                ).first()

                if delega_consigliere_giovane:
                    if delega_consigliere_giovane.persona == persona:
                        esiti += [
                            (
                                persona,
                                sede,
                                "Saltato. E' già Consigliere giovane di questa Sede."
                            )
                        ]
                        continue

                gia_consigliere = persona.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=CONSIGLIERE_GIOVANE, fine=None
                ).first()

                if gia_consigliere:
                    gia_consigliere.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())

                msg = "OK, Nomina effettuata."
            elif nomina == VICE_PRESIDENTE:
                delega_vice_presidente = sede.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=VICE_PRESIDENTE, fine=None
                ).first()

                if delega_vice_presidente:
                    if delega_vice_presidente.persona == persona:
                        esiti += [
                            (
                                persona,
                                sede,
                                "Saltato. E' già Vice Presidente di questa Sede."
                            )
                        ]
                        continue

                gia_consigliere = persona.deleghe_attuali(
                    al_giorno=datetime.datetime.now(), tipo=VICE_PRESIDENTE, fine=None
                ).first()

                if gia_consigliere:
                    gia_consigliere.termina(mittente=me, accoda=True, termina_at=datetime.datetime.now())

                msg = "OK, Nomina effettuata."

            # Crea la nuova delega e notifica.
            delega = Delega(
                persona=persona,
                tipo=nomina,
                oggetto=sede,
                inizio=poco_fa(),
                firmatario=me,
            )

            delega.save()
            delega.invia_notifica_creazione()

            esiti += [
                (persona, sede, msg)
            ]

        moduli += [modulo]

    contesto = {
        "moduli": moduli,
        "numero_presidenti_per_pagina": numero_presidenti_per_pagina,
        "esiti": esiti,
    }

    return 'admin_import_presidenti.html', contesto


@pagina_privata
def admin_pulisci_email(request, me):

    if not me.utenza.is_superuser:
        return redirect(ERRORE_PERMESSI)

    modulo = ModuloPulisciEmail(request.POST or None)
    risultati = []

    if modulo.is_valid():

        indirizzi = modulo.cleaned_data['indirizzi']
        indirizzi = indirizzi.split("\n")

        for indirizzo in indirizzi:

            indirizzo = indirizzo.strip()
            if not indirizzo:  # Salta linee vuote
                continue

            persone = Persona.objects.filter(Q(email_contatto__iexact=indirizzo) | Q(utenza__email__iexact=indirizzo))

            if not persone.exists():

                risultati += [
                    (indirizzo, 'text-danger', "Nessuna utenza trovata per questa e-mail.")
                ]

            else:  # Una o piu' persone ha questo indirizzo e-mail

                for persona in persone:  # Per ogni persona

                    try:
                        delegati = persona.sede_riferimento().delegati_attuali(tipo__in=(UFFICIO_SOCI, UFFICIO_SOCI_UNITA)) |\
                                    persona.sede_riferimento().comitato.delegati_attuali(tipo__in=(UFFICIO_SOCI, PRESIDENTE))
                    except AttributeError:
                        delegati = Persona.objects.none()

                    if not delegati.exists():
                        risultati += [
                            (indirizzo, 'alert-warning', "La persona trovata (%s) non ha delegati a cui notificare la "
                                                        "disattivazione." % persona.codice_fiscale)
                        ]
                        continue

                    email_contatto_corrotta = persona.email_contatto.lower() == indirizzo.lower()
                    try:
                        email_utenza_corrotta = persona.utenza.email.lower() == indirizzo.lower()
                    except:  # Se non ha utenza
                        email_utenza_corrotta = False

                    # Se l'e-mail di contatto e' problematica...
                    if email_contatto_corrotta:

                        msg =   "(GAIA-%s) L'e-mail di contatto (%s) ha avuto un alto tasso di "\
                                "ritorno ed è stata quindi cancellata per tutelare il servizio. "% (
                            poco_fa().strftime("%d/%m/%Y %H:%M"), indirizzo
                        )
                        persona.note = "%s\n\n%s" % (persona.note, msg)
                        persona.email_contatto = ""
                        persona.save()
                        Log.modifica(me, persona, "email_contatto", indirizzo, "")

                    # Se l'e-mail di accesso e' problematica
                    if email_utenza_corrotta:

                        msg =   "(GAIA-%s) L'e-mail di accesso (%s) ha avuto un alto tasso di "\
                                "ritorno ed è stata quindi cancellata l'utenza per tutela re il servizio. "\
                                "E' quindi necessario abilitare l'accesso nuovamente creando delle nuove "\
                                "credenziali per l'utente dalla sezione 'Credenziali' della sua scheda." % (
                            poco_fa().strftime("%d/%m/%Y %H:%M"), indirizzo
                        )
                        persona.note = "%s\n\n%s" % (persona.note, msg)
                        persona.save()
                        persona.utenza.delete()
                        Log.modifica(me, persona, "e-mail utenza", indirizzo, "")

                    # Notifica delegati...
                    if email_utenza_corrotta:
                        Messaggio.costruisci_e_accoda(
                            oggetto="AZIONE NECESSARIA: Credenziali di %s disattivate perché invalide" % persona.nome_completo,
                            modello="email_admin_pulisci_email_utenza.html",
                            corpo={
                                "persona": persona,
                                "vecchia_email": indirizzo,
                                "operatore": me,
                                "operazione_data": oggi()
                            },
                            destinatari=delegati,
                        )
                        risultati += [
                            (indirizzo, 'text-success', "Disattivata utenza per persona %s. "
                                                        "Delegati avvisati per e-mail." % persona.codice_fiscale)
                        ]

                    elif email_contatto_corrotta:
                        Messaggio.costruisci_e_accoda(
                            oggetto="E-mail di contatto di %s non valida" % persona.nome_completo,
                            modello="email_admin_pulisci_email_contatto.html",
                            corpo={
                                "persona": persona,
                                "vecchia_email": indirizzo,
                                "operatore": me,
                                "operazione_data": oggi()
                            },
                            destinatari=delegati,
                        )
                        risultati += [
                            (indirizzo, 'text-success', "Rimossa e-mail di contatto di %s. "
                                                        "Delegati avvisati per e-mail." % persona.codice_fiscale)
                        ]

    contesto = {
        "risultati": risultati,
        "modulo": modulo
    }
    return "admin_pulisci_email.html", contesto
