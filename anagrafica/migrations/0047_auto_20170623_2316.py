# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-06-23 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0046_auto_20170612_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delega',
            name='tipo',
            field=models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UU', 'Ufficio Soci Unità territoriali'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('GR', 'Referente Gruppo'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('CD', 'Responsabile Campagne di raccolta fondi'), ('RC', 'Responsabile Campagna di raccolta fondi')], db_index=True, max_length=2),
        ),
    ]