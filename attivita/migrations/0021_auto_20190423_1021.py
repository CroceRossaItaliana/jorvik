# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-23 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0020_nonsonounbersaglio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonsonounbersaglio',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='anagrafica.Persona'),
        ),
    ]
