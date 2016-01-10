# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.tratti


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0005_auto_20160110_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Riserva',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(null=True, default=None, blank=True, verbose_name='Fine', db_index=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.')),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, base.tratti.ConPDF),
        ),
        migrations.AddField(
            model_name='persona',
            name='note',
            field=models.TextField(null=True, blank=True, max_length=10000, verbose_name='Note aggiuntive'),
        ),
        migrations.AddField(
            model_name='sede',
            name='attiva',
            field=models.BooleanField(default=True, db_index=True, verbose_name='Attiva'),
        ),
    ]
