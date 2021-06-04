from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from anagrafica.models import Persona
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata
from base.models import Allegato
from .forms import ModuloScriviMessaggioConDestinatariVisibili, ModuloScriviMessaggioConDestinatariNascosti
from .models import Messaggio


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
    query = request.GET.get('q')
    filterby = request.GET.get('mailfilterby')

    if direzione == "in-arrivo":
        messaggi = me.posta_in_arrivo(query, filterby)
    else:
        messaggi = me.posta_in_uscita(query, filterby)

    if messaggio_id is None:
        messaggio = None
    else:
        messaggio = get_object_or_404(Messaggio, pk=messaggio_id)

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
        'query': query or '',
        'filterby': filterby or 'oggetto',
    }

    return 'posta.html', contesto


@pagina_privata
def posta_scrivi(request, me):
    MAX_VISIBILI = 20
    MAX_VISIBILI_STR = "%d destinatari selezionati"

    if request.method == 'GET' and 'id' in request.GET:
        elenco_id = request.GET.get('id')
        elenco = request.session["elenco_%s" % (elenco_id,)]
        filtra = request.session.get("elenco_filtra_%s" % (elenco_id,), default="")
        destinatari = elenco.ordina(elenco.risultati())
        if filtra:  # Se keyword specificata, filtra i risultati
            destinatari = elenco.filtra(destinatari, filtra)
    else:
        destinatari = request.session.get('messaggio_destinatari')

    destinatari = destinatari if destinatari else Persona.objects.none()

    # Svuota eventuale sessione
    request.session["messaggio_destinatari"] = None
    request.session["messaggio_destinatari_timestamp"] = None

    destinatari_count = destinatari.count()
    max_visibili_count = MAX_VISIBILI_STR % destinatari_count
    if destinatari:  # Ho appena scaricato i destinatari
        destinatari_list = [x.pk for x in destinatari]
        if destinatari_count > MAX_VISIBILI:
            form = ModuloScriviMessaggioConDestinatariNascosti(initial={'destinatari': destinatari_list,
                'destinatari_selezionati': max_visibili_count})
        else:
            form = ModuloScriviMessaggioConDestinatariVisibili(initial={'destinatari': destinatari_list,})

    else:  # Normale
        if len(request.POST.getlist('destinatari')) > MAX_VISIBILI:
            form = ModuloScriviMessaggioConDestinatariNascosti(
                request.POST or None, request.FILES or None, initial={
                "destinatari_selezionati": max_visibili_count})
        else:
            form = ModuloScriviMessaggioConDestinatariVisibili(request.POST or None, request.FILES or None)

    if form.is_valid():
        cd = form.cleaned_data
        allegati = list()

        for a in cd['allegati']:
            allegato = Allegato(file=a, nome=a.name)
            allegato.scadenza = datetime.now() + timedelta(days=15)
            allegato.save()
            allegati.append(allegato)

        # Invia o accoda il messaggio, a seconda del numero di destinatari.
        if len(cd['destinatari']) > MAX_VISIBILI:
            funzione = Messaggio.costruisci_e_accoda
            azione = "accodato"
        else:
            funzione = Messaggio.costruisci_e_invia
            azione = "inviato"

        messaggio = funzione(
            oggetto=cd['oggetto'],
            modello='email_utente.html',
            corpo={"testo": cd['testo']},
            allegati=allegati,
            mittente=me,
            destinatari=[el if isinstance(el, Persona) else Persona.objects.get(pk=int(el))
                for el in cd['destinatari']
            ],
        )

        # Porta alla schermata del messaggio.
        return redirect("/posta/in-uscita/1/%d/?%s" % (messaggio.pk, azione,))
    return 'posta_scrivi.html', {'modulo': form}
