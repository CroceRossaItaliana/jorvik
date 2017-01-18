from django_cron import CronJobBase, Schedule

from posta.models import Messaggio


class CronSmaltisciCodaPosta(CronJobBase):

    RUN_EVERY_MINS = 21600

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'posta.smaltisci'

    def do(self):
        Messaggio.smaltisci_coda(dimensione_massima=2200)
