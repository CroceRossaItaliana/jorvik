from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def invia_mail(self, pk):

    from posta.models import Messaggio

    messaggio = Messaggio.objects.get(pk=pk)

    # Controlla che il messaggio sia stato inviato
    if messaggio.terminato:
        return

    # Controlla che siamo il task giusto (evita duplicati)
    if messaggio.worker_id != self.request.id:
        logger.error("Worker ID non corrispondente.")
        return

    invio_terminato = messaggio.invia()

    if not invio_terminato:
        logger.error("Errore temporaneo, nuovo tentativo richiesto.")
        raise self.retry()

    # Messaggio inviato con successo.
    messaggio.worker_id = None
    messaggio.save()
