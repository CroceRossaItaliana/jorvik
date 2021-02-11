import json

from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE
from anagrafica.models import Sede, Persona
from anagrafica.permessi.applicazioni import CONSIGLIERE_GIOVANE
from anagrafica.serializers import PersonaSerializer
from autenticazione.models import Utenza


class Command(BaseCommand):

    help = 'Aggiungi curriculum della persona all\'indice inserito'

    def add_arguments(self, parser):
        parser.add_argument('index', nargs='?', type=str, default='')

    def handle(self, *args, **options):
        index = options['index']
        if index:
            count = 0
            for persona in Persona.objects.all():
                s_persona = PersonaSerializer(persona)
                data = json.dumps(s_persona.data)
                print(data)
                if count == 10:
                    break
                else:
                    count += 1
        else:
            print('carica_volontari_elastic [index]')
