# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-30 17:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0069_evento_descrizione'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evento',
            old_name='comitato_organizzativo',
            new_name='sede',
        ),
    ]
