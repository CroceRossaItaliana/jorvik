# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('attivita', '0001_initial'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='locazione',
            field=models.ForeignKey(blank=True, related_name='attivita_attivita', null=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='attivita',
            name='sede',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='attivita'),
        ),
        migrations.AddField(
            model_name='area',
            name='sede',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='aree'),
        ),
    ]
