# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-06-09 11:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0061_auto_20200527_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sede',
            name='sede_operativa',
            field=models.ManyToManyField(blank=True, to='base.Locazione'),
        ),
    ]
