import uuid
from django.core.management import BaseCommand
from anagrafica.models import Persona, Sede


class Command(BaseCommand):

    def handle(self, *args, **options):
        count_persone = 0
        count_sedi = 0
        print('** Signature Persone start')
        for persona in Persona.objects.all():
            persona.signature = uuid.uuid4()
            persona.save()
            count_persone += 1
        print('** Signature Persone finish')

        print('** Signature Sede start')
        for sede in Sede.objects.all():
            sede.signature = uuid.uuid4()
            sede.save()
            count_sedi += 1
        print('** Signature Sede finish')

        print('Persone {} Sedi {}'.format(count_persone, count_sedi))
