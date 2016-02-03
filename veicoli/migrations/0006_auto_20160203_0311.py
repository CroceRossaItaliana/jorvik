# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0005_auto_20160128_0351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collocazione',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='fermotecnico',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
    ]
