from celery import shared_task


@shared_task(bind=True)
def generate_elenco_soci_al_giorno(self, *args):
    from .reports import ReportElencoSoci

    params = args[0]
    report = ReportElencoSoci(from_celery=True)
    report.celery(params)
