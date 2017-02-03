# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.management.base import NoArgsCommand

from anagrafica.models import Sede


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        print('Inizio controllo albero delle sedi')
        Sede.objects.rebuild()
        print('Albero delle sedi corretto')
