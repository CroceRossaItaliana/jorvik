# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0004_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collocazione',
            name='creato_da',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='collocazioni_veicoli', blank=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='fermotecnico',
            name='creato_da',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fermi_tecnici_creati', blank=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='creato_da',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manutenzioni_registrate', blank=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='rifornimento',
            name='creato_da',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rifornimenti_registrate', blank=True, to='anagrafica.Persona'),
        ),
    ]
