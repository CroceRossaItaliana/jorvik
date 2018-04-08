from __future__ import absolute_import

import os
from celery import Celery

from jorvik.settings import CELERY_CONF
from posta.queue import process_queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jorvik.settings')

app = Celery('jorvik')
app.conf.update(CELERY_CONF.items('celery'))

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, process_queue.s(500), name='email queue processor')
