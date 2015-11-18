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
            field=models.ForeignKey(blank=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='attivita_attivita'),
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
