# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-02-25 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0024_auto_20190429_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turno',
            name='nome',
            field=models.CharField(db_index=True, default='Nuovo turno', max_length=256),
        ),
    ]