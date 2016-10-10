# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-18 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0016_invitocorsobase_invitante'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitocorsobase',
            name='automatica',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Automatica'),
        ),
        migrations.AddField(
            model_name='invitocorsobase',
            name='confermata',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Confermata'),
        ),
        migrations.AddField(
            model_name='invitocorsobase',
            name='ritirata',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Ritirata'),
        ),
    ]
