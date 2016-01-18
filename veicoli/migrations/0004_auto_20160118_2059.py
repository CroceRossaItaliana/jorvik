# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0014_auto_20160118_2059'),
        ('veicoli', '0003_auto_20160118_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='rifornimento',
            name='creato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='rifornimenti_registrate', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='collocazione',
            name='autoparco',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='autoparco', to='veicoli.Autoparco'),
        ),
        migrations.AlterField(
            model_name='collocazione',
            name='creato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='collocazioni_veicoli', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='fermotecnico',
            name='creato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='fermi_tecnici_creati', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='manutenzione',
            name='creato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='manutenzioni_registrate', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='manutenzione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='segnalazioni', blank=True, null=True, to='veicoli.Manutenzione'),
        ),
    ]
