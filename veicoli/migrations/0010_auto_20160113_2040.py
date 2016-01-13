# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
        ('veicoli', '0009_auto_20160113_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='collocazione',
            name='creato_da',
            field=models.ForeignKey(related_name='collocazioni_veicoli', null=True, to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='collocazione',
            name='creazione',
            field=models.DateTimeField(db_index=True, auto_now_add=True, default=datetime.datetime(2016, 1, 13, 20, 40, 6, 312505)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collocazione',
            name='ultima_modifica',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2016, 1, 13, 20, 40, 6, 312505), auto_now=True),
            preserve_default=False,
        ),
    ]
