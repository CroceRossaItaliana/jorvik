# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0006_auto_20160203_0311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manutenzione',
            name='costo',
            field=models.FloatField(),
        ),
    ]
