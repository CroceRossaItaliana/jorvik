# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0022_auto_20160128_0351'),
    ]

    operations = [
        migrations.AddField(
            model_name='riserva',
            name='protocollo_data',
            field=models.DateField(verbose_name='Data di presa in carico', null=True),
        ),
        migrations.AddField(
            model_name='riserva',
            name='protocollo_numero',
            field=models.CharField(verbose_name='Numero di protocollo', max_length=512, null=True),
        ),
    ]
