# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.core.management.base import NoArgsCommand
from django.db import transaction

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE
from anagrafica.models import Sede


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        with transaction.atomic():
            comitati = Sede.objects.filter(tipo=Sede.COMITATO, estensione=LOCALE)
            for comitato in comitati:
                if comitato.genitore.estensione == PROVINCIALE and comitato.genitore.genitore and comitato.genitore.genitore.estensione == REGIONALE:
                    comitato.genitore = comitato.genitore.genitore
                    comitato.save()