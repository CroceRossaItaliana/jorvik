# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-06-23 17:18
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('donazioni', '0009_auto_20170621_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donatore',
            name='stato_nascita',
            field=django_countries.fields.CountryField(blank=True, max_length=2, verbose_name='Stato di nascita'),
        ),
    ]
