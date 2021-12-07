import json
import requests

from django.core.management import BaseCommand
from anagrafica.models import Persona
from anagrafica.serializers import CurriculumPersonaSerializer
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('source', nargs='?', type=str, default='')
        parser.add_argument('dest', nargs='?', type=str, default='')

    def handle(self, *args, **options):
        source = options['source']
        dest = options['dest']
        if source and dest:
            pass
        else:
            print('reindex_elastic (source_index) (dest_index)')
