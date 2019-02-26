from django.core.mail import EmailMessage

from celery import shared_task, task

# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)


@shared_task(bind=True)
def send_mail(self, user_pk):
    from .monitoraggio import TypeFormResponses

    responses = TypeFormResponses(user_pk=user_pk)
    pdf = responses.convert_html_to_pdf()

    email = EmailMessage(
        'Subject',
        'message.',
        'from@localhost',  # From
        ['to@localhost']
    )
    email.attach('file.pdf', pdf)
    email.send()
