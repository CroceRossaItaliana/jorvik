# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0003_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quota',
            name='annullato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='quote_annullate', blank=True, null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='quota',
            name='appartenenza',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='quote', null=True, to='anagrafica.Appartenenza'),
        ),
        migrations.AlterField(
            model_name='quota',
            name='registrato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='quote_registrate', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='quota',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quote', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='tesserino',
            name='confermato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='tesserini_confermati', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='tesserino',
            name='emesso_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tesserini_emessi', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='tesserino',
            name='riconsegnato_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='tesserini_riconsegnati', null=True, to='anagrafica.Persona'),
        ),
    ]
