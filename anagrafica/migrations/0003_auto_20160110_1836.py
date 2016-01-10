# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20160110_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='estensione',
            name='motivo',
            field=models.CharField(null=True, max_length=2048),
        ),
        migrations.AlterField(
            model_name='documento',
            name='tipo',
            field=models.CharField(default='I', max_length=1, db_index=True, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale'), ('A', 'Altro')]),
        ),
    ]
