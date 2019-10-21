from django.core.mail import EmailMessage

from celery import shared_task

from jorvik.settings import DEFAULT_FROM_EMAIL


@shared_task(bind=True)
def send_mail(self, user_pk, target):
    from .monitoraggio import MONITORAGGIOTYPE

    responses = MONITORAGGIOTYPE[target][0](user_pk=user_pk)
    pdf = responses.convert_html_to_pdf()
    presidente = responses.persona.sede_riferimento().presidente()

    email = EmailMessage(responses.email_object %
                         responses.persona,
                         responses.email_body,
                         DEFAULT_FROM_EMAIL,
                         [presidente.email],)
    email.attach('file.pdf', pdf)
    email.send()
