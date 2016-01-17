# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0004_auto_20160117_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='protocollo_data',
            field=models.DateField(null=True, verbose_name='Data di presa in carico'),
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='protocollo_numero',
            field=models.CharField(null=True, verbose_name='Numero di protocollo', max_length=512),
        ),
    ]
