# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-11-16 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sala_operativa', '0005_auto_20201113_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='mezzoso',
            name='modello',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='mezzoso',
            name='targa',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
