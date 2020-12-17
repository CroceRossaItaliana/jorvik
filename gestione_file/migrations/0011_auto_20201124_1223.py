# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-11-24 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestione_file', '0010_documentocomitato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentocomitato',
            name='nome',
            field=models.CharField(choices=[('ASSEMBLEA', (('A-A1', 'Avviso convocazione'), ('A-A2', 'Delibere'), ('A-A3', 'Verbali'))), ('CONSIGLIO DIRETTIVO', (('B-B1', 'Avviso convocazione'), ('B-B2', 'Delibere'), ('B-B3', 'Verbali'))), ('PRESIDENTI DIRETTORI', (('C-C1', 'Provvedimenti/Ordinanze'),)), ('REVISIONE DEI CONTI', (('D-D1', 'Verbali, Relazioni e/o altre Comunicazioni del revisore'),)), ('EVENTUALE ORGANO DI CONTROLLO', (('E-E1', 'Verbali, Relazioni e/o Comunicazioni del revisore'),))], max_length=50),
        ),
    ]
