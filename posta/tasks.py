from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def invia_mail(self, pk):
    from posta.models import Messaggio, ErrorePostaTemporaneo, ErrorePostaFatale
    try:
        return Messaggio.invia(pk)
    except ErrorePostaTemporaneo as exc:  # chiede a celery di riprovare fra 5 minui
        logger.error('{}'.format(exc))
        raise self.retry(exc=exc)
    except ErrorePostaFatale:
        pass
    except Exception as e:
        logger.error('Errore imprevisto {}'.format(e))
