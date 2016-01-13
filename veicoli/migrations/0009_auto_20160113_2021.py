# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0008_auto_20160113_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veicolo',
            name='telaio',
            field=models.CharField(max_length=64, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', verbose_name='Numero Identificazione Veicolo (E)', null=True, unique=True, db_index=True),
        ),
    ]
