# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0002_quota_vecchio_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quota',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='tesseramento',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='tesserino',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
