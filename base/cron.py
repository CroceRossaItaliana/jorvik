from django_cron import CronJobBase, Schedule

from formazione.models import Aspirante
from .models import Allegato, Autorizzazione


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


class CronRichiesteInAttesa(CronJobBase):

    RUN_EVERY_HOURS = 24 * 15
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.estensioni.notifica.manuali'

    def do(self):
        Autorizzazione.notifiche_richieste_in_attesa()


class PulisciAspirantiVolontari(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.formazione.cancella_aspiranti_reclamati'

    def do(self):
        print('Inizio cancellazione aspiranti con appartenenze come volontari')
        Aspirante.pulisci_volontari()
        print('Fine cancellazione')
