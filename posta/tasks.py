import traceback

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.template.loader import get_template
from django.utils.text import Truncator

from .models import Messaggio
from anagrafica.models import Persona
from base.models import Allegato


logger = get_task_logger('posta')


@shared_task(ignore_result=True)
def crea_email(oggetto='Nessun oggetto', modello='email_vuoto.html', corpo=None, mittente=None, destinatari=None,
               allegati=None, **kwargs):

    corpo = corpo or {}
    destinatari = destinatari or []
    allegati = allegati or []

    corpo.update({
        'mittente': mittente,
        'allegati': allegati,
    })

    oggetto = Truncator(oggetto).chars(Messaggio.LUNGHEZZA_MASSIMA_OGGETTO)

    with transaction.atomic():
        try:
            mittente = Persona.objects.get(pk=mittente)
        except Persona.DoesNotExist:
            mittente = None

        m = Messaggio(oggetto=oggetto,
                      mittente=mittente,
                      corpo=get_template(modello).render(corpo),
                      **kwargs)
        m.processa_link()
        m.save()

        for d in destinatari:
            m.oggetti_destinatario.create(persona_id=d)

        for a in Allegato.objects.filter(id__in=allegati):
            a.oggetto = m
            a.save()

        return m


@shared_task(ignore_result=True)
def send(pk):
    # noinspection PyBroadException
    try:
        from posta.models import Messaggio
        return Messaggio.invia(pk)
    except Exception as e:
        logger.error(traceback.format_exc())
        return ['FAIL: worker {}'.format(e)]

