# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0004_auto_20150918_1644'),
        ('attivita', '0004_auto_20150918_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='apertura',
            field=models.CharField(default='A', max_length=1, db_index=True, choices=[('C', 'Chiusa'), ('A', 'Aperta')]),
        ),
        migrations.AddField(
            model_name='attivita',
            name='descrizione',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='attivita',
            name='estensione',
            field=models.ForeignKey(null=True, to='anagrafica.Sede', related_name='attivita_estensione', default=None),
        ),
        migrations.AddField(
            model_name='attivita',
            name='stato',
            field=models.CharField(default='B', max_length=1, db_index=True, choices=[('B', 'Bozza'), ('V', 'Visibile')]),
        ),
    ]
