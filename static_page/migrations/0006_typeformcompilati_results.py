# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-07-20 15:56
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_page', '0005_typeformcompilati'),
    ]

    operations = [
        migrations.AddField(
            model_name='typeformcompilati',
            name='results',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]