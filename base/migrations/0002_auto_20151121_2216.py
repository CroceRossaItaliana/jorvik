# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locazione',
            name='civico',
            field=models.CharField(verbose_name='Civico', max_length=16, blank=True),
        ),
        migrations.AlterField(
            model_name='locazione',
            name='provincia',
            field=models.CharField(verbose_name='Provincia', max_length=64, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='locazione',
            name='regione',
            field=models.CharField(verbose_name='Regione', max_length=64, db_index=True, blank=True),
        ),
    ]
