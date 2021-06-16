# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-30 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0069_auto_20201124_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delega',
            name='tipo',
            field=models.CharField(choices=[('PR', 'Presidente'), ('VP', 'Vice Presidente'), ('CM', 'Commissario'), ('CN', 'Consigliere'), ('CG', 'Consigliere giovane'), ('US', 'Ufficio Soci'), ('UM', 'Ufficio Soci corpo militare'), ('IV', 'Ufficio Soci Infermiere volontarie'), ('UU', 'Ufficio Soci Unità territoriali'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('RS', 'Referente Servizio SO'), ('RO', 'Referente Operazione SO'), ('RU', 'Referente Operazione SO'), ('GR', 'Referente Gruppo'), ('CO', 'Delegato Centrale Operativa'), ('SO', 'Delegato Sala Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('RE', 'Responsabile Evento'), ('AP', 'Responsabile Autoparco')], db_index=True, max_length=2),
        ),
    ]
