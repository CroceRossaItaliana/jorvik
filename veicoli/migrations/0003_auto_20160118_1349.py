# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autoparco',
            name='nome',
            field=models.CharField(db_index=True, max_length=256),
        ),
    ]
