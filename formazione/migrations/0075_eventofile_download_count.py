# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-06-10 12:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0074_eventofile_eventolink'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventofile',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
