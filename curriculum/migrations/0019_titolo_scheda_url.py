# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-08-31 09:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0018_titolo_scheda_prevede_esame'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolo',
            name='scheda_url',
            field=models.URLField(blank=True, null=True, verbose_name='Scheda originale'),
        ),
    ]
