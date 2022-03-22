from collections import OrderedDict
from datetime import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import render_to_response, redirect, get_object_or_404

from autenticazione.funzioni import pagina_privata
from autenticazione.models import Utenza
from attivita.forms import ModuloStatisticheAttivitaPersona
from attivita.models import Partecipazione
from attivita.stats import statistiche_attivita_persona
from base.errori import (errore_generico, messaggio_generico,
                         errore_nessuna_appartenenza)
from base.models import Log
from curriculum.models import Titolo, TitoloPersonale
from curriculum.utils import carica_altri_titoli, carica_titolo_studio, carica_conoscenze_linguistiche, \
    carica_esperienza_professionale
from posta.models import Messaggio
from sangue.models import Donatore
from .menu import FORMS, QUALIFICA_CRI, ALTRE_QIALIFICHE, TITOLI_STUDIO, COMPETENZE_LINGUISTICHE, \
    COMPETENZE_PROFESSIONALI
from ..permessi.applicazioni import PRESIDENTE, COMMISSARIO, UFFICIO_SOCI, UFFICIO_SOCI_IIVV, UFFICIO_SOCI_CM
from ..permessi.costanti import (ERRORE_PERMESSI, MODIFICA, LETTURA)
from ..forms import (ModuloCreazioneDocumento, ModuloCreazioneTelefono, ModuloDonatore,
    ModuloDonazione, ModuloNuovaFototessera, ModuloProfiloModificaAnagrafica,
    ModuloProfiloTitoloPersonale, ModuloUtenza, ModuloModificaDataInizioAppartenenza,
    ModuloUSModificaUtenza)
from ..models import (Persona, Appartenenza, ProvvedimentoDisciplinare, Riserva)

from formazione.validators import validate_file_type

@pagina_privata
def profilo(request, me, pk, sezione=None):
    from ..profile.menu import profile_sections, filter_per_role

    persona = get_object_or_404(Persona, pk=pk)
    puo_modificare = me.permessi_almeno(oggetto=persona, minimo=MODIFICA)
    puo_leggere = me.permessi_almeno(oggetto=persona, minimo=LETTURA)
    forced_view = []

    if me.is_responsabile_formazione or me.is_direttore:
        forced_view.append('curriculum')

    # Controlla permessi di visualizzazione
    sezioni = profile_sections(
        puo_leggere, puo_modificare, forced_view=forced_view)
    sezioni = filter_per_role(request, me, persona,
                              sezioni, forced_to_view=len(forced_view) > 0)

    context = {
        "persona": persona,
        "puo_modificare": puo_modificare,
        "puo_leggere": puo_leggere,
        "sezioni": sezioni,
        "attuale": sezione,
    }

    if not sezione:  # Prima pagina
        return 'anagrafica_profilo_profilo.html', context

    else:  # Sezione aperta
        if sezione not in sezioni:
            return redirect(ERRORE_PERMESSI)

        s = sezioni[sezione]
        response = s[2](request, me, persona)
        try:
            f_template, f_context = response
            context.update(f_context)
            return f_template, context
        except ValueError:
            return response


def _profilo_anagrafica(request, me, persona):
    puo_modificare = me.permessi_almeno(persona, MODIFICA)
    modulo = ModuloProfiloModificaAnagrafica(request.POST or None,
                                            me=me,
                                            instance=persona,
                                            prefix="anagrafica")
    modulo_numero_telefono = ModuloCreazioneTelefono(request.POST or None, prefix="telefono")

    if puo_modificare and modulo.is_valid():
        Log.registra_modifiche(me, modulo)
        modulo.save()

    if puo_modificare and modulo_numero_telefono.is_valid():
        persona.aggiungi_numero_telefono(
            modulo_numero_telefono.cleaned_data.get('numero_di_telefono'),
            modulo_numero_telefono.cleaned_data.get('tipologia') == modulo_numero_telefono.SERVIZIO,
        )

    contesto = {
        "modulo": modulo,
        "modulo_numero_telefono": modulo_numero_telefono,
    }
    return 'anagrafica_profilo_anagrafica.html', contesto


def _profilo_appartenenze(request, me, persona):
    puo_modificare = me.permessi_almeno(persona, MODIFICA)

    already_valid = False
    forms = []
    terminabili = []

    for app in persona.appartenenze.all():
        form = None
        terminabile = me.permessi_almeno(app.estensione.first(), MODIFICA)

        for form in forms:
            if not form is None and form.is_valid():
                already_valid = True

        if app.attuale() and app.modificabile() and puo_modificare and not already_valid:
            form = ModuloModificaDataInizioAppartenenza(request.POST or None, instance=app, prefix="%d" % app.pk)

            inizio_pk = "%s-inizio" % app.pk
            fine_pk = "%s-fine" % app.pk

            if inizio_pk in request.POST or fine_pk in request.POST and form.is_valid():
                with transaction.atomic():
                    if app.membro == Appartenenza.DIPENDENTE:
                        app_volontario = persona.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
                        if app_volontario:
                            try:
                                riserva = Riserva.objects.get(appartenenza=app_volontario)
                            except Riserva.DoesNotExist:
                                pass
                            else:
                                riserva.inizio = form.cleaned_data['inizio']
                                riserva.fine = form.cleaned_data['fine']
                                riserva.save()
                    form.save()

        forms += [form]
        terminabili += [terminabile]

    appartenenze = zip(persona.appartenenze.all(), forms, terminabili)

    context = {
        "appartenenze": appartenenze,
        "es": Appartenenza.ESTESO
    }

    return 'anagrafica_profilo_appartenenze.html', context


def _profilo_fototessera(request, me, persona):
    puo_modificare = me.permessi_almeno(persona, MODIFICA)

    modulo = ModuloNuovaFototessera(request.POST or None, request.FILES or None)
    if modulo.is_valid():
        fototessera = modulo.save(commit=False)
        fototessera.persona = persona
        fototessera.save()

        # Ritira eventuali fototessere in attesa
        if persona.fototessere_pending().exists():
            for x in persona.fototessere_pending():
                x.autorizzazioni_ritira()

        Log.crea(me, fototessera)

    contesto = {
        "puo_modificare": puo_modificare,
        "modulo": modulo,
    }
    return 'anagrafica_profilo_fototessera.html', contesto


def _profilo_deleghe(request, me, persona):
    return 'anagrafica_profilo_deleghe.html', {}


def _profilo_turni(request, me, persona):
    modulo = ModuloStatisticheAttivitaPersona(request.POST or None)
    storico = Partecipazione.objects.filter(persona=persona).order_by('-turno__inizio')
    statistiche = statistiche_attivita_persona(persona, modulo)
    contesto = {
        "storico": storico,
        "statistiche": statistiche,
        "statistiche_modulo": modulo,
    }
    return 'anagrafica_profilo_turni.html', contesto


def _profilo_riserve(request, me, persona):

    riserve = Riserva.objects.filter(persona=persona)

    contesto = {
        "riserve": riserve,
    }


    return 'anagrafica_profilo_riserve.html', contesto


def _profilo_curriculum(request, me, persona):
    from curriculum.forms import FormAddQualificaCRI, FormAddTitoloStudio, FormAddAltreQualifica
    deleghe_list = me.deleghe_attuali(tipo__in=[PRESIDENTE, COMMISSARIO, UFFICIO_SOCI, UFFICIO_SOCI_IIVV, UFFICIO_SOCI_CM])
    delega_crea_qualifica_cri = me.can_create_qualifica_cri
    puoi_modificare = me.permessi_almeno(oggetto=persona, minimo=LETTURA)
    non_puo_fare_niente = me.permessi_almeno(oggetto=persona, minimo=MODIFICA)

    reversed = reverse('profilo:profilo', args=[persona.pk, 'curriculum'])
    redirect_url = redirect(reversed)

    modifica = request.GET.get('modifica', '')

    form = FORMS[modifica][0] if FORMS[modifica] else None
    not_upload_file=False

    if request.method == 'POST':
        if modifica == QUALIFICA_CRI:
            form = form(request.POST, request.FILES, me=persona)
            if form.is_valid():
                cd = form.cleaned_data
                cd['creatore']=me
                if validate_file_type(request.FILES['attestato_file']) == False:
                    not_upload_file = True
                    context = {
                        "modulo": form,
                        "pk": persona.pk,
                        "sezione": "curriculum",
                        "puo_modificare": puoi_modificare if deleghe_list else non_puo_fare_niente,
                        "tipo_titolo": FORMS[modifica][1] if FORMS[modifica] else None,
                        "can_create_qualifica_cri": delega_crea_qualifica_cri,
                        "not_upload_file": not_upload_file,
                    }
                    messages.error(request,
                                   "Tipo di file non supportato. Tipi di file supportati: csv, zip, rar, gif, png, jpg,  jpeg, tiff, rtf, pdf, ods, odt, doc, docx, xls, xlsx.")
                    return 'anagrafica_profilo_curriculum.html', context

                qualifica_created = TitoloPersonale.crea_qualifica_regressa(persona=persona, to_responsabile=True, **cd)
                if not qualifica_created:
                    messages.error(request, 'Errore.')
                    return errore_nessuna_appartenenza(request, me, torna_url=reversed)

                messages.success(request, "La qualifica è stata inserita.")
                return redirect_url

            messages.success(request, "La qualifica non è stata inserita.")
        elif modifica == ALTRE_QIALIFICHE:
            not_upload_file=carica_altri_titoli(request, persona, redirect_url)
        elif modifica == TITOLI_STUDIO:
            not_upload_file=carica_titolo_studio(request, persona, redirect_url)
        elif modifica == COMPETENZE_LINGUISTICHE:
            not_upload_file=carica_conoscenze_linguistiche(request, persona, redirect_url)
        elif modifica == COMPETENZE_PROFESSIONALI:
            not_upload_file=carica_esperienza_professionale(request, persona, redirect_url)

    else:
        # FORM VUOTO
        form = form() if form else None

    context = {
        "modulo": form,
        "pk": persona.pk,
        "sezione": "curriculum",
        "puo_modificare": puoi_modificare if deleghe_list else non_puo_fare_niente,
        "tipo_titolo": FORMS[modifica][1] if FORMS[modifica] else None,
        "can_create_qualifica_cri": delega_crea_qualifica_cri,
        "not_upload_file":not_upload_file,
    }
    return 'anagrafica_profilo_curriculum.html', context


def _profilo_sangue(request, me, persona):
    modulo_donatore = ModuloDonatore(request.POST or None, prefix="donatore", instance=Donatore.objects.filter(persona=persona).first())
    modulo_donazione = ModuloDonazione(request.POST or None, prefix="donazione")

    if modulo_donatore.is_valid():
        donatore = modulo_donatore.save(commit=False)
        donatore.persona = persona
        donatore.save()

    if modulo_donazione.is_valid():
        donazione = modulo_donazione.save(commit=False)
        donazione.persona = persona
        r = donazione.save()

    contesto = {
        "modulo_donatore": modulo_donatore,
        "modulo_donazione": modulo_donazione,
    }

    return 'anagrafica_profilo_sangue.html', contesto


def _profilo_documenti(request, me, persona):
    puo_modificare = me.permessi_almeno(persona, MODIFICA)
    modulo = ModuloCreazioneDocumento(request.POST or None, request.FILES or None)
    if puo_modificare and modulo.is_valid():
        f = modulo.save(commit=False)
        f.persona = persona
        f.save()

    contesto = {
        "modulo": modulo,
    }
    return 'anagrafica_profilo_documenti.html', contesto


def _profilo_provvedimenti(request, me, persona):
        provvedimenti = ProvvedimentoDisciplinare.objects.filter(persona=persona)
        contesto = {
            "provvedimenti": provvedimenti,
        }

        return 'anagrafica_profilo_provvedimenti.html', contesto


def _profilo_quote(request, me, persona):
    contesto = {}
    return 'anagrafica_profilo_quote.html', contesto


def _profilo_credenziali(request, me, persona):
    utenza = Utenza.objects.filter(persona=persona).first()

    modulo_utenza = modulo_modifica = None
    if utenza:
        modulo_modifica = ModuloUSModificaUtenza(request.POST or None, instance=utenza)
    else:
        modulo_utenza = ModuloUtenza(request.POST or None, instance=utenza, initial={"email": persona.email_contatto})

    if modulo_utenza and modulo_utenza.is_valid():
        utenza = modulo_utenza.save(commit=False)
        utenza.persona = persona
        utenza.save()
        utenza.genera_credenziali()
        return redirect(persona.url_profilo_credenziali)

    if modulo_modifica and modulo_modifica.is_valid():
        vecchia_email_contatto = persona.email
        vecchia_email = Utenza.objects.get(pk=utenza.pk).email
        nuova_email = modulo_modifica.cleaned_data.get('email')

        if vecchia_email == nuova_email:
            return errore_generico(request, me, titolo="Nessun cambiamento",
                                   messaggio="Per cambiare indirizzo e-mail, inserisci un "
                                             "indirizzo differente.",
                                   torna_titolo="Credenziali",
                                   torna_url=persona.url_profilo_credenziali)

        if Utenza.objects.filter(email__icontains=nuova_email).first():
            return errore_generico(request, me, titolo="E-mail già utilizzata",
                                   messaggio="Esiste un altro utente in Gaia che utilizza "
                                             "questa e-mail (%s). Impossibile associarla quindi "
                                             "a %s." % (nuova_email, persona.nome_completo),
                                   torna_titolo="Credenziali",
                                   torna_url=persona.url_profilo_credenziali)

        def _invia_notifica():
            Messaggio.costruisci_e_invia(
                oggetto="IMPORTANTE: Cambio e-mail di accesso a Gaia (credenziali)",
                modello="email_credenziali_modificate.html",
                corpo={
                    "vecchia_email": vecchia_email,
                    "nuova_email": nuova_email,
                    "persona": persona,
                    "autore": me,
                },
                mittente=me,
                destinatari=[persona],
                utenza=True
            )

        _invia_notifica()  # Invia notifica alla vecchia e-mail
        Log.registra_modifiche(me, modulo_modifica)
        modulo_modifica.save()  # Effettua le modifiche
        persona.refresh_from_db()
        if persona.email != vecchia_email_contatto:  # Se e-mail principale cambiata
            _invia_notifica()  # Invia la notifica anche al nuovo indirizzo

        return messaggio_generico(request, me, titolo="Credenziali modificate",
                                  messaggio="Le credenziali di %s sono state correttamente aggiornate." % persona.nome,
                                  torna_titolo="Credenziali",
                                  torna_url=persona.url_profilo_credenziali)

    contesto = {
        "utenza": utenza,
        "modulo_creazione": modulo_utenza,
        "modulo_modifica": modulo_modifica

    }
    return 'anagrafica_profilo_credenziali.html', contesto
