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

    RUN_EVERY_HOURS = 2
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.autorizzazioni.automatiche'

    def do(self):
        Autorizzazione.gestisci_automatiche()


class CronTrasferimentiAutoInAttesa(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.trasferimenti.notifica.automatici'

    def do(self):
        Autorizzazione.notifiche_trasferimenti_pending_automatici()


class CronTrasferimentiManualiInAttesa(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.trasferimenti.notifica.manuali'

    def do(self):
        Autorizzazione.notifiche_trasferimenti_pending_manuali()


class CronEstensioniInAttesa(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.estensioni.notifica.manuali'

    def do(self):
        Autorizzazione.notifiche_estensioni_pending()
