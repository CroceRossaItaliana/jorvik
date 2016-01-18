# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gruppi', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appartenenza',
            name='negato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='appartenenze_gruppi_negate', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='gruppo',
            name='area',
            field=models.ForeignKey(related_name='gruppi', null=True, to='attivita.Area'),
        ),
        migrations.AlterField(
            model_name='gruppo',
            name='attivita',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='gruppi', null=True, to='attivita.Attivita'),
        ),
    ]
