# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0012_auto_20160113_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rifornimento',
            name='contalitri',
            field=models.FloatField(db_index=True, verbose_name='(c/o Cisterna int.) Contalitri', default=None, null=True),
        ),
    ]
