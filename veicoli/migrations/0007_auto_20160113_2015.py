# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0006_auto_20160113_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veicolo',
            name='carrozzeria',
            field=models.CharField(max_length=32, help_text='es. Chiuso', verbose_name='Carrozzeria (J.2)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='categoria',
            field=models.CharField(help_text='es. Ambulanza', max_length=32, db_index=True, verbose_name='Categoria del Veicolo (J)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='libretto',
            field=models.CharField(help_text='Formato 201X-XXXXXXXXX', max_length=32, db_index=True, verbose_name='N. Libretto'),
        ),
    ]
