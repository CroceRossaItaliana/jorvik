import uuid
from time import sleep

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from anagrafica.models import Persona, Sede


class Command(BaseCommand):

    DEFAULT_BATCH_SIZE = 200

    def add_arguments(self, parser):
        parser.add_argument('batch_size', nargs='?', type=int, default=self.DEFAULT_BATCH_SIZE)

    def handle(self, *args, **options):
        count_persone = 0
        count_sedi = 0
        batch_size = options['batch_size']

        print('** Signature Persone start')
        persone_all = Persona.objects.all()
        persone_paginator = Paginator(persone_all, batch_size)

        for num_page in persone_paginator.page_range:
            for persona in persone_paginator.page(num_page):
                persona.signature = uuid.uuid4()
                persona.save()
                count_persone += 1
            sleep(30)
        print('** Signature Persone finish')

        print('** Signature Sede start')
        
        sedi_all = Sede.objects.all()
        sedi_paginator = Paginator(sedi_all, batch_size)

        for num_page in sedi_paginator.page_range:
            for sede in sedi_paginator.page(num_page):
                sede.signature = uuid.uuid4()
                sede.save()
                count_persone += 1
            sleep(30)
        print('** Signature Sede finish')

        print('Persone {} Sedi {}'.format(count_persone, count_sedi))
