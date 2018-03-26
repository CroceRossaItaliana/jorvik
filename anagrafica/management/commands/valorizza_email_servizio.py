# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.management.base import BaseCommand

from anagrafica.models import Persona


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--dryrun', type=bool, default=False)

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Valuto email di servizio gia' presenti..."))
        persone = Persona.objects.all()
        aggiornati = 0
        totali = len(persone)

        dryrun = options.get('dryrun')

        for p in persone:
            if not p.ha_email_servizio:
                if not dryrun:
                    p.aggiorna_email_servizio()

                aggiornati += 1

        self.stdout.write(self.style.SUCCESS("Valutate %s persone. Cambiate %s. "
                                             "Dryrun: %s" % (totali, aggiornati, dryrun)))