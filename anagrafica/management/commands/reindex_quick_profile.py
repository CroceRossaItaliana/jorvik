import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from anagrafica.models import Persona
from anagrafica.utils import quick_profile_feeding


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = []

        """
        persone = Persona.objects.filter(utenza__email__in=['marialetizia.vella@toscana.cri.it',
                                                            'account4.test@cri.it',
                                                            'account3.test@cri.it',
                                                            'account2.test@cri.it',
                                                            'account1.test@cri.it',
                                                            'andrea.carmisciano@citelgroup.it'])
        """
        persone = Persona.objects.all()
        done = 0
        for pp in persone:
            quick_profile_feeding(pp)
            done += 1

        print('done: {}'.format(done))
