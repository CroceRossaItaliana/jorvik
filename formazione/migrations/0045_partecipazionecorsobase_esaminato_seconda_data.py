# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-07-10 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0044_corsobase_data_esame_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='esaminato_seconda_data',
            field=models.BooleanField(default=False),
        ),
    ]
