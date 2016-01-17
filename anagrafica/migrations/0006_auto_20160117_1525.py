# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0005_auto_20160117_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dimissione',
            name='fine',
        ),
        migrations.RemoveField(
            model_name='dimissione',
            name='inizio',
        ),
        migrations.AddField(
            model_name='dimissione',
            name='creazione',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 17, 15, 25, 45, 354990), auto_now_add=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dimissione',
            name='ultima_modifica',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 17, 15, 25, 48, 843289), auto_now=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='registrato_da',
            field=models.ForeignKey(default=1, related_name='provvedimenti_registrati', to='anagrafica.Persona'),
            preserve_default=False,
        ),
    ]
