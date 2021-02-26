# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-10-14 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0021_auto_20191014_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolopersonale',
            name='tipo_documentazione',
            field=models.CharField(blank=True, choices=[('a', 'Attestato'), ('b', 'Brevetto'), ('v', "Verbale d'esame"), ('d', 'Altro documento inerente al corso')], max_length=2, null=True),
        ),
    ]