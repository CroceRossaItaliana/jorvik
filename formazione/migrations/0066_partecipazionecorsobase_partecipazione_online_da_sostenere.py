# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-02-02 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0065_corsobase_data_esame_pratica'),
    ]

    operations = [
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='partecipazione_online_da_sostenere',
            field=models.BooleanField(default=False),
        ),
    ]
