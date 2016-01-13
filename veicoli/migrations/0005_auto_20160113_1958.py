# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0004_auto_20160113_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veicolo',
            name='targa',
            field=models.CharField(db_index=True, verbose_name='Targa (A)', max_length=16, help_text='Targa del Veicolo, senza spazi.'),
        ),
    ]
