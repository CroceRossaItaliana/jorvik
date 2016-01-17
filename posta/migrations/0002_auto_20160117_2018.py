# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posta', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destinatario',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='messaggio',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
