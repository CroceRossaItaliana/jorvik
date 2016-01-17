# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titolopersonale',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
