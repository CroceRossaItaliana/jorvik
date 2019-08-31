# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-11-14 14:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0024_auto_20181113_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='corsobase',
            name='max_participants',
            field=models.SmallIntegerField(default=50, verbose_name='Massimo partecipanti'),
        ),
        migrations.AddField(
            model_name='corsobase',
            name='min_participants',
            field=models.SmallIntegerField(default=20, validators=[django.core.validators.MinValueValidator(20)], verbose_name='Minimo partecipanti'),
        ),
        migrations.AlterField(
            model_name='formazionetitlegoal',
            name='unit_reference',
            field=models.CharField(blank=True, choices=[('1', 'Salute'), ('2', 'Sociale'), ('3', 'Emergenza)'), ('4', 'Advocacy e mediazione umanitaria'), ('5', 'Giovani'), ('6', 'Sviluppo')], max_length=3, null=True, verbose_name='Unità riferimento'),
        ),
    ]
