# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-09-16 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0053_merge'),
        ('formazione', '0055_lezionecorsobase_docente_esterno'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lezionecorsobase',
            name='docente',
        ),
        migrations.AddField(
            model_name='lezionecorsobase',
            name='docente',
            field=models.ManyToManyField(to='anagrafica.Persona', verbose_name='Docente della lezione'),
        ),
    ]
