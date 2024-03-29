# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-10-05 15:16
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0059_auto_20200626_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corsoestensione',
            name='segmento',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('VM', 'Operatore Villa Maraini'), ('SC', 'Volontario in servizio civile universale')], max_length=100),
        ),
    ]
