# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-03-22 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posta', '0011_messaggio_priorita'),
    ]

    operations = [
        migrations.AddField(
            model_name='messaggio',
            name='utenza',
            field=models.BooleanField(default=False),
        ),
    ]