# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-18 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0041_titolopersonale_codice_albo'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolopersonale',
            name='skills',
            field=models.ManyToManyField(blank=True, to='curriculum.TitoloSkill'),
        ),
        migrations.AddField(
            model_name='titolopersonale',
            name='specializzazione',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='curriculum.TitoloSpecializzazione'),
        ),
    ]
