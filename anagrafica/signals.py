import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from kombu import uuid

from anagrafica.models import Persona, Appartenenza, Sede
from anagrafica.serializers import CurriculumPersonaSerializer, PersonaSerializer, ComitatoSerializer
from anagrafica.tasks import load_elastic, delete_elastic
from anagrafica.utils import quick_profile_feeding
from jorvik.settings import (
    ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, ELASTIC_PERSONA_INDEX,
    ELASTIC_COMITATO_INDEX, ELASTIC_ACTIVE
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Persona)
def save_persona(sender, instance, **kwargs):
    # also update quickprofile even if elastic is not active
    quick_profile_feeding(instance)

    if ELASTIC_ACTIVE:
        logger.info('Signal post_save Persona id:{} signature:{}'.format(instance.id, instance.signature))

        # Aggiorna curriculum index
        s_curriculum = CurriculumPersonaSerializer(instance)
        load_elastic.apply_async(args=(s_curriculum.data, ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX), task_id=uuid())
        logger.info('task elastic update/create curriculum')

        # Aggiorna persona index
        s_persona = PersonaSerializer(instance)
        load_elastic.apply_async(args=(s_persona.data, ELASTIC_HOST, ELASTIC_PERSONA_INDEX), task_id=uuid())
        logger.info('task elastic update/create persona')


@receiver(post_save, sender=Appartenenza)
def save_appartenenza(sender, instance, **kwargs):
    if ELASTIC_ACTIVE:
        logger.info('Signal post_save Anagrafica id:{} signature:{}'.format(instance.persona.id, instance.persona.signature))

        s_persona = CurriculumPersonaSerializer(instance.persona)
        load_elastic.apply_async(args=(s_persona.data, ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX), task_id=uuid())
        logger.info('task elastic update/create curriculum')


@receiver(post_save, sender=Sede)
def save_sade(sender, instance, **kwargs):
    if ELASTIC_ACTIVE:
        logger.info('Signal post_save Sede id:{} signature:{}'.format(instance.id, instance.signature))

        s_sede = ComitatoSerializer(instance)
        load_elastic.apply_async(args=(s_sede.data, ELASTIC_HOST, ELASTIC_COMITATO_INDEX), task_id=uuid())
        logger.info('task elastic update/create sede')


@receiver(post_delete, sender=Sede)
def delete_sade(sender, instance, **kwargs):
    if ELASTIC_ACTIVE:
        logger.info('Signal post_delete Sede id:{} signature:{}'.format(instance.id, instance.signature))
        delete_elastic.apply_async(args=(ELASTIC_HOST, ELASTIC_COMITATO_INDEX, instance.signature), task_id=uuid())

        logger.info('task elastic delete sede')


@receiver(post_delete, sender=Persona)
def delete_persona(sender, instance, **kwargs):
    if ELASTIC_ACTIVE:
        signature = instance.signature
        logger.info('Signal post_delete Persona id:{} signature:{}'.format(instance.id, signature))
        delete_elastic.apply_async(args=(ELASTIC_HOST, ELASTIC_PERSONA_INDEX, signature), task_id=uuid())
        logger.info('task elastic delete Persona')

        delete_elastic.apply_async(args=(ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX, signature), task_id=uuid())
        logger.info('task elastic delete Curriculum')
