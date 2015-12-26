from django.db.models.loading import get_model
from django.shortcuts import redirect

from anagrafica.permessi.costanti import ERRORE_PERMESSI, MODIFICA
from autenticazione.funzioni import pagina_privata
from social.models import Commento


@pagina_privata
def commenti_nuovo(request, me):
    """
    Crea un nuovo commento e ritorna indietro alla pagina dei commenti.
    :return:
    """

    if not request.method == 'POST':
        return redirect(ERRORE_PERMESSI)

    next = request.POST['next']
    oggetto_app_label = request.POST['oggetto_app_label']
    oggetto_model = request.POST['oggetto_model']
    commento = request.POST['commento']
    oggetto_pk = int(request.POST['oggetto_pk'])

    oggetto_m = get_model(oggetto_app_label, oggetto_model)
    oggetto = oggetto_m.objects.get(pk=oggetto_pk)

    if not hasattr(oggetto, 'commenti'):
        return redirect(ERRORE_PERMESSI)

    if not commento:
        return redirect(next)

    c = Commento(
        oggetto=oggetto,
        autore=me,
        commento=commento,
    )
    c.save()

    if oggetto.commento_notifica_destinatari(me).exists():
        from posta.models import Messaggio
        Messaggio.costruisci_e_accoda(
            oggetto="Commento di %s su %s" % (me.nome_completo, oggetto,),
            modello="email_commento.html",
            corpo={
                "commento": c,
            },
            mittente=me,
            destinatari=oggetto.commento_notifica_destinatari(me),
        )

    return redirect(next)

@pagina_privata
def commenti_cancella(request, me, pk):
    """
    Cancella un commento, se permesso, e torna indietro.
    :param request:
    :param me:
    :param pk:
    :return:
    """
    c = Commento.objects.get(pk=pk)
    if not (me == c.autore or me.permessi_almeno(c.oggetto, MODIFICA)):
        return redirect(ERRORE_PERMESSI)

    c.delete()
    return redirect(request.GET['next'])
