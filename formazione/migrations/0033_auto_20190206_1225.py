# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-02-06 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0032_corsobase_delibera_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='corsobase',
            name='cdf_area',
            field=models.CharField(blank=True, choices=[('1', 'Salute'), ('2', 'Sociale'), ('3', 'Emergenza'), ('4', 'Principi e Valori'), ('5', 'Giovani'), ('6', 'Sviluppo'), ('7', 'Migrazioni'), ('8', 'Cooperazioni Internazionali')], max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='corsobase',
            name='cdf_level',
            field=models.CharField(blank=True, choices=[('1', 'I Livello'), ('2', 'II Livello'), ('3', 'III Livello'), ('4', 'IV Livello')], max_length=3, null=True),
        ),
    ]