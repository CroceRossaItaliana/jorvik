# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0011_auto_20160113_2301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rifornimento',
            name='conducente',
        ),
        migrations.RemoveField(
            model_name='rifornimento',
            name='numero',
        ),
        migrations.RemoveField(
            model_name='rifornimento',
            name='segnalazione',
        ),
    ]
