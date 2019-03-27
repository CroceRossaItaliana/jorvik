from django.core.mail import EmailMessage

from celery import shared_task

from jorvik.settings import DEFAULT_FROM_EMAIL


@shared_task(bind=True)
def send_mail(self, user_pk):
    from .monitoraggio import TypeFormResponses

    responses = TypeFormResponses(user_pk=user_pk)
    pdf = responses.convert_html_to_pdf()
    presidente = responses.persona.sede_riferimento().presidente()

    email_body = "email_body"
    email = EmailMessage('Risposte monitoraggio 2018 di %s' % responses.persona,
        email_body,
        DEFAULT_FROM_EMAIL,
        [presidente.email],)
    email.attach('file.pdf', pdf)
    email.send()
