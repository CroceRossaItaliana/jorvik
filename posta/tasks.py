from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def invia_mail(self, pk):

    from posta.models import Messaggio

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
