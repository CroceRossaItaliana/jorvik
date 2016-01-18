# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0012_statoaut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cognome',
            field=models.CharField(max_length=64, db_index=True, verbose_name='Cognome'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='nome',
            field=models.CharField(max_length=64, db_index=True, verbose_name='Nome'),
        ),
    ]
