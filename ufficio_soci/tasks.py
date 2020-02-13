from datetime import timedelta, datetime

from celery import shared_task
from celery.task import periodic_task

from ufficio_soci.models import ReportElenco


@shared_task(bind=True)
def generate_elenco(self, *args):
    from .reports import ReportElencoSoci

    params, report_id = args[0], args[1]
    report = ReportElencoSoci(from_celery=True)
    report.celery(params, report_id)


@periodic_task(run_every=timedelta(seconds=86400))  # 24h
def delete_generated_elenco_files():
    delta = datetime.today() - timedelta(hours=24)

    files_to_delete = ReportElenco.objects.filter(creazione__lt=delta)
    [file.file.delete() for file in files_to_delete]  # delete files from filesystem

    files_to_delete.delete()  # then delete records from db
