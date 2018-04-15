from __future__ import absolute_import

import os
from celery import Celery

from jorvik.settings import CELERY_CONF
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jorvik.settings')

app = Celery('jorvik')
app.conf.update(CELERY_CONF.items('celery'))
app.conf.task_routes = {
    'posta.queue.rischedula_invii_falliti': {'queue': 'coda_email_rischedula'},
    'posta.tasks.invia_mail': {'queue': 'coda_email_invio'}
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from posta.queue import rischedula_invii_falliti
    # definisco il task periodico come app level
    task = app.task(rischedula_invii_falliti, bind=True, ignore_results=True)
    sender.add_periodic_task(CELERY_CONF.getint('cleanup', 'periodo'),
                             task.s(CELERY_CONF.getint('cleanup', 'limite')),
                             name='coda rischedula invii falliti')
