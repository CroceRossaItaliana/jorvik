# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0002_auto_20150824_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='nome',
            field=models.CharField(default='Generale', db_index=True, max_length=64),
        ),
        migrations.AddField(
            model_name='area',
            name='obiettivo',
            field=models.SmallIntegerField(default=1, db_index=True),
        ),
    ]
