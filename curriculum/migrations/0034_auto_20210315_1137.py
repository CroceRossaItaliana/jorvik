# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-15 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0033_auto_20210315_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titolo',
            name='tipo',
            field=models.CharField(choices=[('CP', 'Competenza Personale'), ('PP', 'Patente Civile'), ('PC', 'Patente CRI'), ('TS', 'Titolo di Studio'), ('TC', 'Qualifica CRI'), ('AT', 'Altra Qualifica'), ('CL', 'Conoscenze Linguistiche')], db_index=True, max_length=2),
        ),
    ]
