# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0022_auto_20160121_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='riserva',
            name='protocollo_data',
            field=models.DateField(null=True, verbose_name='Data di presa in carico'),
        ),
        migrations.AddField(
            model_name='riserva',
            name='protocollo_numero',
            field=models.CharField(max_length=512, null=True, verbose_name='Numero di protocollo'),
        ),
    ]
