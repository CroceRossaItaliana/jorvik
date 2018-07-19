from celery import uuid
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def rischedula_invii_falliti(self, massimo_messaggi=None):
    """
    Un task celery per riaccodare l'invio di tutti i messaggi che non sono stati inviati,
     e non sono attualmente in coda per l'invio (ad esempio, in seguito allo svuotamento
     della coda di posta).

    :param self:                Task celery.
    :param massimo_messaggi:    Il numero massimo di messaggi da riaccodare per l'invio.
    """
    from .models import Messaggio
    from .tasks import invia_mail

    riaccodati = 0
    non_riaccodati = 0

    # Per ognuno dei messaggi in coda
    for messaggio in Messaggio.in_coda():

        # Assicuriamoci di avere l'ultima copia del messaggio
        messaggio.refresh_from_db()
        logger.debug("Controllo messaggio id=%d" % (messaggio.pk,))

        # Se il messaggio ha un task_id associato, assicuriamoci che il task sia in esecuzione
        task = None
        if messaggio.task_id is not None:
            # Controlla lo stato del task Celery
            # http://docs.celeryproject.org/en/latest/reference/celery.result.html#celery.result.AsyncResult.state
            task = self.app.AsyncResult(messaggio.task_id)
            if task.state in ("QUEUED", "STARTED", "RETRY", "FAILURE", "SUCCESS"):
                # Il task e' ancora in coda. Ignora.
                non_riaccodati += 1
                logger.debug("Task (id=%s) gia' in corso - Ignoro." % (messaggio.task_id,))
                continue

            # Dimentichiamoci del task che e' morto
            assert task.state == "PENDING"
            logger.warning("Task (id=%s) apparentemente morto (%s). Dimentica e riavvia." % (messaggio.task_id,
                                                                                             task.state))
            task.forget()

        # Il task e' morto. Ad esempio, la coda e' stata svuotata.
        # Creiamo un nuovo task ID e riaccodiamo il task.
        messaggio.task_id = uuid()
        messaggio.save()

        logger.warning("Nuovo task per l'invio accodato con id=%s." % (messaggio.task_id,))
        invia_mail.apply_async((messaggio.pk,), task_id=messaggio.task_id)

        riaccodati += 1

    return "%d gia' in invio, %d riaccodati per l'invio" % (non_riaccodati, riaccodati)
