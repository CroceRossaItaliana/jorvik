from django_cron import CronJobBase, Schedule

from attivita.models import Partecipazione
from centrale_operativa.models import Turno as Coturno


class CronCancellaCoturniInvalidi(CronJobBase):

    RUN_AT_TIMES = ['06:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'centrale_operativa.turni.invalidi'

    def do(self):
        turni_da_smontare = Coturno.objects.filter(smontato_da__isnull=True)
        for coturno in turni_da_smontare:
            partecipazione = Partecipazione.objects.filter(turno=coturno.turno,
                                                           persona=coturno.persona).first()
            if not partecipazione:
                coturno.delete()

