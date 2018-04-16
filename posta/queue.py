from celery import uuid
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def rischedula_invii_falliti(self, limit=None):
    from django.db import transaction, DatabaseError
    from .models import Messaggio
    from .tasks import invia_mail

    messaggi = Messaggio.objects.filter(task_id__isnull=False)
    if limit is not None:
        messaggi = messaggi[:limit]

    rischedulati = 0

    for messaggio in messaggi:
        try:
            task = self.app.AsyncResult(messaggio.task_id)
            if not task.failed():
                continue

            # per sicurezza creo un nuovo task_id
            task_id = uuid()
            with transaction.atomic():
                try:
                    messaggio = Messaggio.objects.select_for_update(nowait=True).get(pk=messaggio.pk)
                except DatabaseError:   # per qualche motivo un worker ci sta lavorando
                    continue
                messaggio.task_id = task_id
                messaggio.save()

            # pulisco i risultati precedenti
            task.forget()

            invia_mail.apply_async((messaggio.pk,), task_id=messaggio.task_id)
            rischedulati += 1
        except Exception as e:
            logger.error(e)
            return -1
    return rischedulati
