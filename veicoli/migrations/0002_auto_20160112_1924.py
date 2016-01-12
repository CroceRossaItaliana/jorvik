# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import veicoli.validators


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='immatricolazione',
            name='richiedente',
        ),
        migrations.RemoveField(
            model_name='immatricolazione',
            name='ufficio',
        ),
        migrations.RemoveField(
            model_name='immatricolazione',
            name='veicolo',
        ),
        migrations.RemoveField(
            model_name='veicolo',
            name='formato_targa',
        ),
        migrations.AddField(
            model_name='autoparco',
            name='nome',
            field=models.CharField(max_length=256, default='Autoparco senza nome'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='autoparco',
            name='telefono',
            field=models.CharField(max_length=64, blank=True, verbose_name='Telefono'),
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='data',
            field=models.DateField(validators=[veicoli.validators.valida_data_manutenzione], default="1942-12-12"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='tipo',
            field=models.CharField(choices=[('R', 'Revisione veicolo'), ('M', 'Manutenzione veicolo')], max_length=1, db_index=True, default='M'),
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='manutenzioni', default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rifornimento',
            name='presso',
            field=models.CharField(choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], max_length=1, default=None, verbose_name='Presso', null=True),
        ),
        migrations.DeleteModel(
            name='Immatricolazione',
        ),
    ]
