# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-29 16:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0067_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='stato',
            field=models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('T', 'Terminato'), ('X', 'Annullato')], default='P', max_length=1, verbose_name='Stato'),
        ),
    ]
