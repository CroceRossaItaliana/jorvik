# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-12-14 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0063_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corsobase',
            name='tipo',
            field=models.CharField(blank=True, choices=[('BA', 'Corso di Formazione per Volontari CRI'), ('C1', 'Altri Corsi'), ('CO', 'Corsi online'), ('CE', 'Corsi equipollenza')], max_length=4, verbose_name='Tipo'),
        ),
    ]
