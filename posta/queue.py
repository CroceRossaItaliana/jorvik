import traceback

from celery import shared_task, group
from celery.utils.log import get_task_logger

logger = get_task_logger('posta:coda')


@shared_task(ignore_result=True)
def process_queue(limit=None):
    from .models import Messaggio
    from .tasks import send
    # noinspection PyBroadException
    try:
        msgids = Messaggio.get_email_batch(limit=limit)
    except Exception:
        logger.error(traceback.format_exc())
        return -1

    # fuori lock
    count = len(msgids)
    if count:
        logger.debug('Processing %d messages', count)
        tasks = group(send.s(pk) for pk in msgids)
        tasks.delay()
    return count
