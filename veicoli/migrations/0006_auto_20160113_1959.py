# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0005_auto_20160113_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veicolo',
            name='num_assi',
            field=models.PositiveIntegerField(default=2, verbose_name='Num. Assi (L)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='posti',
            field=models.PositiveIntegerField(default=5, verbose_name='N. Posti a sedere conducente compreso (S.1)'),
        ),
    ]
