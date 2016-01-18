# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0003_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aree', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='attivita',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='attivita', null=True, to='attivita.Area'),
        ),
        migrations.AlterField(
            model_name='attivita',
            name='estensione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, related_name='attivita_estensione', null=True, to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='attivita',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attivita', to='anagrafica.Sede'),
        ),
    ]
