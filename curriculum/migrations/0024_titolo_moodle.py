# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-11-19 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0023_titolo_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolo',
            name='moodle',
            field=models.BooleanField(default=False),
        ),
    ]