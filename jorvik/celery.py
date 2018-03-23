from __future__ import absolute_import

import os
import traceback
from celery import Celery, group
from celery.utils.log import get_task_logger
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jorvik.settings')

app = Celery('jorvik')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

logger = get_task_logger(__name__)


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, process_queue.s(500), name='email queue processor')


@app.task(ignore_result=True)
def send(pk):
    # noinspection PyBroadException
    try:
        from posta.models import Messaggio
        return Messaggio.invia(pk)
    except Exception as e:
        logger.error(traceback.format_exc())
        return ['FAIL: worker {}'.format(e)]


def get_email_batch(limit=None):
    from posta.models import Messaggio
    with transaction.atomic():
        # purtroppo skip_locked è stata inserita solo dalla version 1.11
        query = '''SELECT id FROM posta_messaggio WHERE terminato is NULL ORDER BY priorita'''
        if limit is not None:
            query += ' LIMIT %s'
            limit = (limit,)
        query += ' FOR UPDATE SKIP LOCKED'
        return [msg.pk for msg in Messaggio.objects.raw(query, limit)]


@app.task(ignore_result=True)
def process_queue(limit=None):
    # noinspection PyBroadException
    try:
        msgids = get_email_batch(limit=limit)
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
