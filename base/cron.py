from django_cron import CronJobBase, Schedule

from formazione.models import Aspirante
from anagrafica.models import Riserva
from .models import Allegato, Autorizzazione
from posta.models import Messaggio

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


class CronRichiesteTitoliRegressoInAttesa(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.estensioni.notifica.manuali'

    def do(self):
        Autorizzazione.avviso_richieste_in_attesa_presa_visione_qualifica_cri()


class PulisciAspirantiVolontari(CronJobBase):

    RUN_EVERY_HOURS = 24
    RUN_EVERY_MINS = RUN_EVERY_HOURS * 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.formazione.cancella_aspiranti_reclamati'

    def do(self):
        print('Inizio cancellazione aspiranti con appartenenze come volontari')
        Aspirante.pulisci_volontari()
        print('Fine cancellazione')

#https://django-cron.readthedocs.io/en/latest/installation.html
class EmailAutomaticaFineRiserva(CronJobBase):

    #RUN_EVERY_HOURS = 24
    #RUN_EVERY_MINS = RUN_EVERY_HOURS * 60
    RUN_EVERY_MINS = 1  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'base.formazione.cancella_aspiranti_reclamati'

    def do(self):
        import datetime
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        start_date = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        end_date = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        riserve_terminate=Riserva.objects.filter(fine__range=(start_date, end_date))
        print(riserve_terminate)
        print(len(riserve_terminate))
        for i in riserve_terminate:
            print(i)
            try:
                i.persona.deleghe.last().sede.last().presidente()
            except:
                continue
            #import pdb
            #pdb.set_trace()
            Messaggio.costruisci_e_invia(
                oggetto="Riserva terminata",
                modello="email_automatica_riserva_terminata.html",
                corpo={
                    "riserva": "Riserva terminata. {} {} è di nuovo disponibile.".format(i.persona.nome, i.persona.cognome),
                },
                mittente=i.persona,
                destinatari=[i.persona.deleghe.last().sede.last().presidente(), i.persona.deleghe.last().sede.last().delegati_ufficio_soci()
                ]
            )
            print("OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")

