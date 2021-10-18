# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-09-10 16:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0081_btn_cri_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delega',
            name='tipo',
            field=models.CharField(choices=[('PR', 'Presidente'), ('VP', 'Vice Presidente'), ('CM', 'Commissario'), ('CN', 'Consigliere'), ('CG', 'Consigliere Rappresentante dei Giovani'), ('CC', 'Consigliere Rappresentante dei Giovani Cooptato'), ('US', 'Ufficio Soci'), ('UM', 'Ufficio Soci corpo militare'), ('IV', 'Ufficio Soci Infermiere volontarie'), ('UU', 'Ufficio Soci Unità territoriali'), ('DA', "Delegato d'Area"), ('O1', 'Salute'), ('O2', 'Inclusione Sociale'), ('O3', 'Operazione, Emergenza e Soccorso'), ('O4', 'Principi e Valori Umanitari'), ('O5', 'Coordinatore attività per i Giovani'), ('O6', 'Innovazione, Volontariato e Formazione'), ('O7', 'Cooperazione internazionale decentrata'), ('O8', 'Riduzione del rischio da disastri e resilienza'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('RS', 'Referente Servizio SO'), ('RO', 'Referente Operazione SO'), ('RU', 'Referente Operazione SO'), ('GR', 'Referente Gruppo'), ('CO', 'Delegato Centrale Operativa'), ('SO', 'Delegato Sala Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('EF', 'Responsabile Evento'), ('AP', 'Responsabile Autoparco'), ('RZ', 'Referente Zoom')], db_index=True, max_length=2),
        ),
    ]
