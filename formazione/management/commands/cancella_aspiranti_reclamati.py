# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.management.base import NoArgsCommand

from formazione.models import Aspirante


class Command(NoArgsCommand):
    help = 'Questo comando cancella gli aspiranti già volontari marcando l\'eventuale partecipazione ' \
           'al corso base come superata con successo'

    def handle_noargs(self, **options):
        print('Inizio cancellazione aspiranti con appartenenze come volontari')
        Aspirante.pulisci_volontari()
        print('Fine cancellazione')
