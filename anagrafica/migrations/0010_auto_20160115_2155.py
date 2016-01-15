# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import anagrafica.validators
import base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sospensione',
            name='provvedimento',
        ),
        migrations.RemoveField(
            model_name='sospensione',
            name='provvedimentodisciplinare_ptr',
        ),
        migrations.DeleteModel(
            name='Sospensione',
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='fine',
            field=models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, default=None, blank=True, verbose_name='Fine', db_index=True),
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='inizio',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 15, 21, 55, 33, 559870), verbose_name='Inizio', db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='persona',
            name='codice_fiscale',
            field=base.utils.UpperCaseCharField(db_index=True, validators=[anagrafica.validators.valida_codice_fiscale], verbose_name='Codice Fiscale', unique=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='tipo',
            field=models.CharField(default='A', max_length=1, choices=[('A', 'Ammonizione'), ('S', 'Sospensione'), ('E', 'Esplusione')]),
        ),
    ]
