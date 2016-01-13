# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0003_autoparco_locazione'),
    ]

    operations = [
        migrations.RenameField(
            model_name='veicolo',
            old_name='regine',
            new_name='regime',
        ),
        migrations.RemoveField(
            model_name='rifornimento',
            name='consumo_olio_i',
        ),
        migrations.RemoveField(
            model_name='rifornimento',
            name='consumo_olio_m',
        ),
        migrations.RemoveField(
            model_name='rifornimento',
            name='consumo_olio_t',
        ),
        migrations.AddField(
            model_name='fermotecnico',
            name='motivo',
            field=models.CharField(max_length=512, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='costo',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='descrizione',
            field=models.CharField(max_length=2048, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='km',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='manutentore',
            field=models.CharField(max_length=512, help_text='es. autoriparato', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='numero_fattura',
            field=models.CharField(max_length=20, help_text='es. 122/A', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rifornimento',
            name='costo',
            field=models.FloatField(default=1, verbose_name='Costo', db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='tipo',
            field=models.CharField(max_length=1, default='O', choices=[('R', 'Revisione veicolo'), ('O', 'Manutenzione ordinaria veicolo'), ('S', 'Manutenzione straordinaria veicolo')], db_index=True),
        ),
        migrations.AlterField(
            model_name='rifornimento',
            name='consumo_carburante',
            field=models.FloatField(help_text='Litri di carburante immessi', verbose_name='Consumo carburante lt.', db_index=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='alimentazione',
            field=models.CharField(max_length=1, default=None, choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], null=True, verbose_name='Alimentazione (P.3)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='stato',
            field=models.CharField(max_length=2, default='OK', choices=[('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], verbose_name='Stato'),
        ),
    ]
