from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE
from anagrafica.models import Sede
from anagrafica.permessi.applicazioni import CONSIGLIERE_GIOVANE
from autenticazione.models import Utenza


class Command(BaseCommand):

    INDICE = 'indice'

    help = 'Aggiungi curriculum della persona all\'indice {}'.format(INDICE)

    def handle(self, *args, **options):
        print('handle')
