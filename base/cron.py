from django_cron import CronJobBase, Schedule

from base.models import Allegato, Autorizzazione


class CronCancellaFileScaduti(CronJobBase):

    RUN_EVERY_HOURS = 6
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.allegati.pulisci'

    def do(self):
        n = Allegato.pulisci()
        print("Sono stati rimossi %d file scaduti." % n)

class CronApprovaNegaAuto(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.autorizzazioni.automatiche'

    def do(self):
        n, m = Autorizzazione.gestisci_automatiche()
