# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime
from optparse import make_option

import xlrd
from xlrd.sheet import ctype_text
from django.core.management.base import BaseCommand

from anagrafica.models import Sede, Persona, Appartenenza
from autenticazione.models import Utenza
from base.utils import poco_fa


class Command(BaseCommand):
    args = '<import_file_name>'
    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Dry run'),
    )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        if dry_run:
            self.stdout.write(self.style.NOTICE('Dry run'))

        fname = args[0]
        xl_workbook = xlrd.open_workbook(fname)

        sede = Sede.objects.get(pk=1)

        sheet_names = xl_workbook.sheet_names()
        print('Sheet Names', sheet_names)

        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        c = xl_sheet.cell
        for row_idx in range(1, xl_sheet.nrows):
            _data_nascita = xlrd.xldate.xldate_as_datetime(float(c(row_idx, 3).value), xl_workbook.datemode)
            _inizio_appartenenza = xlrd.xldate.xldate_as_datetime(float(c(row_idx, 4).value), xl_workbook.datemode)
            note = "{} \n\r {}".format(c(row_idx, 8).value, c(row_idx, 8).value)
            nome, cognome, cf, data_nascita, inizio_appartenenza, status, email_contatto, note = c(row_idx, 1).value, c(row_idx, 1).value,\
                                                                                           c(row_idx, 2).value, _data_nascita,\
                                                                                           _inizio_appartenenza, Appartenenza.DIPENDENTE,\
                                                                                           c(row_idx, 6).value, note

            campi_persona = ["nome", "cognome", "codice_fiscale", "data_nascita", "email_contatto", "note"]

            _row_dict = dict(nome=nome, cognome=cognome, codice_fiscale=cf, data_nascita=data_nascita,
                             inizio_appartenenza=inizio_appartenenza, status=status, email_contatto=email_contatto)

            _row = "Nome: {nome} Cognome: {cognome} CF: {codice_fiscale} Nascita: {data_nascita} " \
                   "Init: {inizio_appartenenza} Status: {status} email_contatto: {email_contatto}".format(**_row_dict)
            print(_row)
            persona_dict = dict()
            for l in campi_persona: persona_dict.update({l: _row_dict.get(l)})

            try:
                persona = Persona.objects.get(codice_fiscale__iexact=cf)
            except Persona.DoesNotExist:
                persona = Persona(**persona_dict)
                if dry_run:
                    self.stdout.write(self.style.NOTICE('Dry run skip creating persona'))
                if not dry_run:
                    persona.save()

            for app in persona.appartenenze_attuali():
                app.fine = poco_fa()
                app.save()

            if dry_run:
                self.stdout.write(self.style.NOTICE('Dry run skip creating apertenenza to {}'.format(sede)))
            if not dry_run:
                Appartenenza.objects.create(persona=persona, sede=sede, inizio=inizio_appartenenza,
                                            membro=Appartenenza.DIPENDENTE)

            if not Utenza.objects.filter(persona=persona).exists():
                # Non ha utenza
                if not Utenza.objects.filter(email__iexact=email_contatto):
                    # Non esiste, prova a creare
                    u = Utenza(persona=persona, email=email_contatto)
                    if dry_run:
                        self.stdout.write(self.style.NOTICE('Dry run skip creating user'))
                    if not dry_run:
                        u.save()
                        u.genera_credenziali()
