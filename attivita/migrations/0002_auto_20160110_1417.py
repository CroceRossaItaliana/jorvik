# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
        ('attivita', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='locazione',
            field=models.ForeignKey(to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, related_name='attivita_attivita', null=True, blank=True),
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
