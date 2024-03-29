from __future__ import absolute_import
import os

from celery import Celery, current_app
from celery.signals import after_task_publish

from .settings import CELERY_CONF


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jorvik.settings')

app = Celery('jorvik')
app.conf.update(CELERY_CONF.items('celery'))
app.conf.broker_transport_options = { 'master_name': os.environ.get('REDIS_MASTER', "django") }
app.conf.result_backend_transport_options = { 'master_name': os.environ.get('REDIS_MASTER', "django") }

# Per favore, ricordati di aggiornare anche i seguenti file:
# - /docker-compose.yml
app.conf.task_routes = {
    'posta.queue.rischedula_invii_falliti': {'queue': 'coda_email_rischedula'},
    'posta.tasks.invia_mail': {'queue': 'coda_email_invio'},
    'posta.tasks.invia_mail_forzato': {'queue': 'coda_email_invio'},

    'ufficio_soci.tasks.delete_generated_elenco_files': {'queue': 'periodic_ufficio_soci'},
    'ufficio_soci.tasks.generate_elenco': {'queue': 'shared_ufficio_soci'},

    'static_page.tasks.send_mail': {'queue': 'queue_monitoraggio'},
    'static_page.tasks.send_mail_regionale': {'queue': 'queue_monitoraggio'},

    'formazione.tasks.task_invia_email_agli_aspiranti': {'queue': 'queue_formazione'},
    'formazione.tasks.task_invia_email_apertura_evento': {'queue': 'queue_formazione'},

    'anagrafica.tasks.load_elastic': {'queue': 'queue_elastic'},
    'anagrafica.tasks.delete_elastic': {'queue': 'queue_elastic'},
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from posta.queue import rischedula_invii_falliti
    # definisco il task periodico come app level
    task = app.task(rischedula_invii_falliti, bind=True, ignore_results=True)
    sender.add_periodic_task(CELERY_CONF.getint('riaccoda', 'periodo'),
                             task.s(),
                             name='task: riaccoda messaggi')


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    """
    Questo segnale si occupa di cambiare lo stato di un task che e' stato aggiunto
     in coda a "QUEUED". Questo ci permette di disinguere i task che sono stati
     accodati, da quelli che non esistono "PENDING", poiche' Celery e' ottimista
     e rispondera' sempre "PENDING" per i task che non sono "ancora" esistenti.
    """
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
    backend.store_result(headers['id'], None, "QUEUED")
