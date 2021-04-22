from celery import shared_task
from celery.utils.log import get_task_logger

from base.classes.tasks import TransactionAwareTask

logger = get_task_logger(__name__)


@shared_task(bind=True, base=TransactionAwareTask)
def invia_mail(self, pk):
    from .models import Messaggio

    messaggio = Messaggio.objects.get(pk=pk)
    logger.info("messaggio id=%d" % pk)

    # Controlla che il messaggio sia stato inviato
    if messaggio.terminato:
        logger.warning("Il messaggio e' gia' stato inviato. Esco.")
        return

    # Controlla che siamo il task giusto (evita duplicati)
    if messaggio.task_id != self.request.id:
        logger.warning("Worker ID non corrispondente. Possibile duplicato. Esco.")
        return

    invio_terminato = messaggio.invia()

    if not invio_terminato:
        logger.error("Errore temporaneo, nuovo tentativo richiesto.")
        raise self.retry()

    # Messaggio inviato con successo.
    logger.info("Messaggio inviato. Rimuovo task_id e salvo.")
    messaggio.task_id = None
    messaggio.save()


@shared_task(bind=True, base=TransactionAwareTask)
def invia_mail_forzato(self, pk_tuple):
    """
    Questo task invia forzatamente la mail.
    Nessuna verifica si fa se il messaggio è stato precedentemente inviato
    oppure sia accodato. (come con l'invio normale nella funzione di sopra)
    """
    from celery import uuid
    from celery.result import AsyncResult
    from .models import Messaggio

    logger = get_task_logger(__name__)
    rescheduled_tasks_id = list()

    messages_to_resend = Messaggio.objects.filter(pk__in=pk_tuple)
    for msg in messages_to_resend:
        pk = msg.pk

        logger.info("[forced] Controllo messaggio id=%d" % pk)

        # Controllo se il messaggio ha un task_id,
        # se presente - dimentico il task per assegnare un nuovo task_id al messaggio
        if msg.task_id is not None:
            task = AsyncResult(msg.task_id)
            task.forget()
            logger.info("[forced] Dimentico task_id %s per il messaggio id=%d" % (msg.task_id, pk))

        # Creiamo un nuovo task ID e riaccodiamo il task.
        msg.task_id = uuid()
        msg.save()

        logger.warning("[forced] Nuovo task per l'invio accodato con id=%s." % msg.task_id)

        is_sent = msg.invia(forced=True)
        if not is_sent:
            logger.error("[forced] Errore temporaneo, nuovo tentativo richiesto.")
            raise self.retry()

        # Messaggio inviato con successo.
        logger.info("[forced] Messaggio %s inviato. Rimuovo task_id e salvo." % msg.pk)

        rescheduled_tasks_id.append(msg.task_id)
        msg.task_id = None

        msg.save()

    return len(rescheduled_tasks_id)
