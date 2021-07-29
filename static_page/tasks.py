from django.core.mail import EmailMessage

from celery import shared_task

from jorvik.settings import DEFAULT_FROM_EMAIL


@shared_task(bind=True)
def send_mail(self, request, user_pk, target):
    from .monitoraggio import MONITORAGGIOTYPE

    responses = MONITORAGGIOTYPE[target][0](request=request, user_pk=user_pk)
    pdf = responses.convert_html_to_pdf()
    presidente = responses.persona.sede_riferimento().presidente()

    email = EmailMessage(responses.email_object %
                         responses.persona,
                         responses.email_body,
                         DEFAULT_FROM_EMAIL,
                         [presidente.email],)
    email.attach('file.pdf', pdf)
    email.send()


@shared_task(bind=True)
def send_mail_regionale(self, request, user_pk, target):
    from .monitoraggio import MONITORAGGIOTYPE, MONITORAGGIO_TRASPARENZA

    responses = MONITORAGGIOTYPE[target][0](request=request, user_pk=user_pk)
    pdf = responses.convert_html_to_pdf()

    sede_regionale = responses.comitato.sede_regionale
    sede_regionale_email = sede_regionale.email if hasattr(sede_regionale, 'email') else None

    email = EmailMessage(responses.email_object %
                         responses.persona,
                         responses.email_body_regionale.format(responses.comitato),
                         DEFAULT_FROM_EMAIL,
                         [sede_regionale_email],)

    email.attach('file.pdf', pdf)
    email.send()
