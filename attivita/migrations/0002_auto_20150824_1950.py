# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
        ('attivita', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='locazione',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attivita_attivita', to='base.Locazione'),
        ),
        migrations.AddField(
            model_name='attivita',
            name='sede',
            field=models.ForeignKey(related_name='attivita', to='anagrafica.Sede'),
        ),
        migrations.AddField(
            model_name='area',
            name='sede',
            field=models.ForeignKey(related_name='aree', to='anagrafica.Sede'),
        ),
    ]
