# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0003_auto_20150918_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='nome',
            field=models.CharField(db_index=True, max_length=256, default='Generale'),
        ),
    ]
