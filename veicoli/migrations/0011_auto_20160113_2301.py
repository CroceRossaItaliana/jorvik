# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import veicoli.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
        ('veicoli', '0010_auto_20160113_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='manutenzione',
            name='creato_da',
            field=models.ForeignKey(default=1, related_name='manutenzioni_registrate', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='data',
            field=models.DateField(db_index=True, validators=[veicoli.validators.valida_data_manutenzione]),
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='descrizione',
            field=models.TextField(max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='numero_fattura',
            field=models.CharField(max_length=64, help_text='es. 122/A'),
        ),
    ]
