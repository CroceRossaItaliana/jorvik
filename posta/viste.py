import math
from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.shortcuts import redirect

from anagrafica.models import Persona
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata
from base.models import Allegato
from posta.forms import ModuloScriviMessaggioConDestinatariVisibili, \
    ModuloScriviMessaggioConDestinatariNascosti
from posta.models import Messaggio


__author__ = "alfioemanuele"

"""
Questo file contiene le viste relative al modulo di posta
"""

POSTA_PER_PAGINA = 7

def posta_home(request):
    """
    Questo metodo viene chiamato se non viene specificata la direzione (ie /posta/).
    Redirige alla direzione di default (/posta/in-arrivo/).
    :return:
    """
    return redirect('/posta/in-arrivo/')

@pagina_privata
def posta(request, me, direzione="in-arrivo", pagina=1, messaggio_id=None):
    """
    Questa vista gestisce la casella di posta.
    :param direzione: 'in-arrivo' per la posta in entrata o altro per la posta in uscita.
    :param pagina: Un numero di pagina per la paginazione.
    :param messaggio_id: ID del messaggio da aprire, None altrimenti.
    :return:
    """

    if direzione == "in-arrivo":
        messaggi = me.posta_in_arrivo()
    else:
        messaggi = me.posta_in_uscita()

    if messaggio_id is None:
        messaggio = None
    else:
        messaggio = Messaggio.objects.get(pk=messaggio_id)

        # Controlla che io abbia i permessi per leggere il messaggio:
        #  - Devo essere o mittente o destinatario
        #  - Se vista "in-uscita", controllo di essere davvero il mittente
        #     (in quanto saro' in grado di leggere l'elenco dei destinatari).
        if me != messaggio.mittente and not messaggio.destinatario(me):
            return redirect(ERRORE_PERMESSI)

        if not direzione == "in-arrivo" and not me == messaggio.mittente:
            return redirect("/posta/in-arrivo/1/" + str(messaggio_id) + "/")

    pagina = int(pagina)
    if pagina < 0:
        pagina = 1

    p = Paginator(messaggi, POSTA_PER_PAGINA)
    pg = p.page(pagina)

    contesto = {
        'direzione': direzione,
        'pagina': pagina,
        'pagine': p.num_pages,
        'totale': p.count,
        'messaggi': pg.object_list,
        'messaggio': messaggio,
        'ha_precedente': pg.has_previous(),
        'ha_successivo': pg.has_next(),
        'pagina_precedente': pagina-1,
        'pagina_successiva': pagina+1,
        'inviato': 'inviato' in request.GET,
        'accodato': 'accodato' in request.GET,
    }

    return 'posta.html', contesto



@pagina_privata
def posta_scrivi(request, me):

    destinatari = Persona.objects.none()

    # Prova a recuperare destinatari dalla sessione.
    try:
        timestamp = request.session["messaggio_destinatari_timestamp"]
        if timestamp and timestamp > (datetime.now() - timedelta(seconds=10)):
            # max 10 secondi fa
            destinatari = request.session["messaggio_destinatari"]

    except KeyError:
        # Nessun destinatario in sessione.
        pass

    # Svuota eventuale sessione
    request.session["messaggio_destinatari"] = None
    request.session["messaggio_destinatari_timestamp"] = None

    MAX_VISIBILI = 20
    MAX_VISIBILI_STR = "%d destinatari selezionati"

    if destinatari:  # Ho appena scaricato i destinatari

        if destinatari.count() > MAX_VISIBILI:
            modulo = ModuloScriviMessaggioConDestinatariNascosti(initial={
                "destinatari": [x.pk for x in destinatari], "destinatari_selezionati": MAX_VISIBILI_STR % (destinatari.count(),)
            })

        else:
            modulo = ModuloScriviMessaggioConDestinatariVisibili(initial={
                "destinatari": [x.pk for x in destinatari],
            })

    else:  # Normale
        if len(request.POST.getlist('destinatari')) > MAX_VISIBILI:
            modulo = ModuloScriviMessaggioConDestinatariNascosti(request.POST or None, request.FILES or None, initial={
                "destinatari_selezionati": MAX_VISIBILI_STR % (destinatari.count(),)
            })

        else:
            modulo = ModuloScriviMessaggioConDestinatariVisibili(request.POST or None,  request.FILES or None)

    if modulo.is_valid():

        allegati = []
        for a in modulo.cleaned_data['allegati']:
            ai = Allegato(file=a, nome=a.name)
            ai.scadenza = datetime.now() + timedelta(days=15)
            ai.save()
            allegati.append(ai)

        messaggio = Messaggio.costruisci(
            oggetto=modulo.cleaned_data['oggetto'],
            modello='email_utente.html',
            corpo={"testo": modulo.cleaned_data['testo']},
            allegati=allegati,
            mittente=me,
            destinatari=[
                el if isinstance(el, Persona) else Persona.objects.get(pk=int(el))
                for el in modulo.cleaned_data['destinatari']
            ],
        )

        # Invia o accoda il messaggio, a seconda del numero di destinatari.
        if len(modulo.cleaned_data['destinatari']) > MAX_VISIBILI:
            messaggio.accoda()
            azione = "accodato"

        else:
            messaggio.invia()
            azione = "inviato"

        # Porta alla schermata del messaggio.
        return redirect("/posta/in-uscita/1/%d/?%s" % (messaggio.pk, azione,))

    contesto = {
        "modulo": modulo,
    }

    return 'posta_scrivi.html', contesto
