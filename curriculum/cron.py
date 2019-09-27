# from django_cron import CronJobBase, Schedule
# from posta.models import Messaggio
# from jorvik.settings import DEFAULT_FROM_EMAIL
# from .models import TitoloPersonale


# class CronCheckExpiredCourseTitles(CronJobBase):
#     RUN_EVERY_HOURS = 23
#     RUN_EVERY_MINS = RUN_EVERY_HOURS * 60
#
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'curriculum.check_expired_course_titles'
#
#     def do(self):
#         titles = TitoloPersonale.get_expired_course_titles()
#         if titles:
#             for title in titles:
#                 persona = title.persona
#                 email = persona.utenza.email
#                 Messaggio.costruisci_e_accoda(
#                     oggetto="Il tuo titolo %s è scaduto." % title.titolo.nome,
#                     modello="email_expired_course_titolo_personale.html",
#                     corpo={
#                         'title': title,
#                         'persona': persona,
#                     },
#                     destinatari=[persona],
#                 )
#             print('Sono stati notificati degli utenti con dei titoli del corso scaduti.')
