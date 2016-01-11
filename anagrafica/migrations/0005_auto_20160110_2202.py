# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0004_remove_estensione_attuale'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estensione',
            name='protocollo_numero',
            field=models.CharField(blank=True, null=True, verbose_name='Numero di protocollo', max_length=512),
        ),
    ]
