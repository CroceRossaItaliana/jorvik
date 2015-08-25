import math
from django.core.paginator import Paginator
from django.shortcuts import redirect
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata
from posta.models import Messaggio

__author__ = "alfioemanuele"

"""
Questo file contiene le viste relative al modulo di posta
"""

POSTA_PER_PAGINA = 7

def posta_home(request, me):
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
        if me != messaggio.mittente and me not in messaggio.destinatari:
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
    }

    return 'posta.html', contesto