# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0005_auto_20150918_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='nome',
            field=models.CharField(max_length=255, db_index=True, default='Nuova attività'),
        ),
    ]
